import json
import re
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from src.assistant import OpenAICompatibleClient, SAPTicketAssistant


class FakeLLM:
    def __init__(self, *, source_id=None, response=None):
        self.calls = []
        self.source_id = source_id
        self.response = response

    def complete(self, system, user):
        self.calls.append((system, user))
        if self.response is not None:
            return self.response
        source_id = self.source_id or re.search(r"\[ID: ([^\]]+)\]", user).group(1)
        return json.dumps({
            "summary": "Possível divergência na determinação da estratégia de liberação.",
            "probable_causes": ["Verificar os critérios de liberação descritos na fonte."],
            "checks": ["Consultar o status e os dados do pedido sem alterar o documento."],
            "questions": [],
            "risks": [],
            "source_ids": [source_id],
            "confidence": "medium",
            "human_review_required": False,
        })


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        kb = self.root / "knowledge"
        kb.mkdir()
        (kb / "approval.md").write_text(
            "# Estratégia de liberação de pedido de compra\n\n"
            "Se a liberação do pedido de compra falhar, conferir os critérios de estratégia, "
            "dados do documento e status de aprovação antes de qualquer mudança.\n\n"
            "Fonte: https://help.sap.com/docs/example/approval",
            encoding="utf-8",
        )
        self.kb = kb
        self.log = self.root / "logs" / "requests.jsonl"

    def tearDown(self):
        self.temp.cleanup()

    def test_grounded_answer_returns_existing_source_and_logs(self):
        llm = FakeLLM()
        assistant = SAPTicketAssistant(self.kb, self.log, llm)
        result = assistant.answer("No pedido de compra 4500000123, a liberação falha com erro de estratégia de aprovação não determinada.")
        self.assertEqual(result["status"], "answered")
        self.assertEqual(result["process"], "purchase_order")
        self.assertEqual(result["sources"][0]["path"], "approval.md")
        self.assertEqual(result["sources"][0]["urls"], ["https://help.sap.com/docs/example/approval"])
        self.assertFalse(result["human_review_required"])
        self.assertEqual(len(llm.calls), 1)
        self.assertIn("approval.md", llm.calls[0][1])
        record = json.loads(self.log.read_text(encoding="utf-8"))
        self.assertEqual(record["response"]["request_id"], result["request_id"])

    def test_vague_ticket_asks_for_details_without_calling_llm(self):
        llm = FakeLLM()
        result = SAPTicketAssistant(self.kb, self.log, llm).answer("Erro no pedido de compra")
        self.assertEqual(result["status"], "needs_info")
        self.assertTrue(result["questions"])
        self.assertEqual(llm.calls, [])

    def test_out_of_scope_includes_sap_business_one(self):
        llm = FakeLLM()
        result = SAPTicketAssistant(self.kb, self.log, llm).answer("SAP Business One: erro ao gravar pedido de compra")
        self.assertEqual(result["status"], "out_of_scope")
        self.assertEqual(llm.calls, [])

    def test_no_matching_evidence_escalates(self):
        llm = FakeLLM()
        result = SAPTicketAssistant(self.kb, self.log, llm).answer("Na entrada de mercadorias 5000000123 o lote série não aparece e ocorre erro de determinação de depósito.")
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertTrue(result["human_review_required"])
        self.assertEqual(llm.calls, [])

    def test_invalid_citation_cannot_ground_an_answer(self):
        response = json.dumps({"summary": "Uma solução", "probable_causes": ["Causa"], "checks": ["Alterar"], "questions": [], "risks": [], "source_ids": ["fabricated"], "confidence": "high", "human_review_required": False})
        result = SAPTicketAssistant(self.kb, self.log, FakeLLM(response=response)).answer("No pedido de compra 4500000123, a liberação falha com erro de estratégia de aprovação não determinada.")
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertEqual(result["probable_causes"], [])
        self.assertTrue(result["human_review_required"])

    def test_risky_request_requires_human_and_removes_mutating_check(self):
        response = json.dumps({"summary": "Investigar liberação", "probable_causes": [], "checks": ["Executar SQL UPDATE direto no banco de dados.", "Consultar status do pedido."], "questions": [], "risks": [], "source_ids": ["approval-1"], "confidence": "high", "human_review_required": False})
        result = SAPTicketAssistant(self.kb, self.log, FakeLLM(response=response)).answer("No pedido de compra 4500000123, a liberação falha com erro de aprovação; posso executar SQL UPDATE direto no banco?")
        self.assertEqual(result["status"], "human_review")
        self.assertTrue(result["human_review_required"])
        self.assertEqual(result["confidence"], "low")
        self.assertEqual(result["checks"], [])
        self.assertNotIn("SQL", result["summary"])

    def test_llm_unsafe_output_in_any_field_is_blocked(self):
        unsafe_by_field = {
            "summary": "Execute SQL UPDATE direto no banco e libere a fatura.",
            "probable_causes": ["Altere a tolerância em produção."],
            "checks": ["Libere o pedido agora."],
            "questions": ["Desbloqueie a fatura agora?"],
            "risks": ["Estorne o documento em produção."],
        }
        for field, unsafe_value in unsafe_by_field.items():
            with self.subTest(field=field):
                payload = {"summary": "Investigar a falha.", "probable_causes": [], "checks": ["Consultar status do pedido."], "questions": [], "risks": [], "source_ids": ["approval-1"], "confidence": "high", "human_review_required": False}
                payload[field] = unsafe_value
                result = SAPTicketAssistant(self.kb, self.log, FakeLLM(response=json.dumps(payload))).answer("No pedido de compra 4500000123, a liberação falha com erro de estratégia de aprovação não determinada.")
                self.assertEqual(result["status"], "human_review")
                self.assertTrue(result["human_review_required"])
                self.assertEqual(result["probable_causes"], [])
                self.assertEqual(result["checks"], [])
                self.assertNotIn("SQL", result["summary"])

    def test_confidence_cannot_be_high_without_live_sap_verification(self):
        response = json.dumps({"summary": "Hipótese condicionada", "probable_causes": [], "checks": ["Consultar status do pedido."], "questions": [], "risks": [], "source_ids": ["approval-1"], "confidence": "high", "human_review_required": False})
        result = SAPTicketAssistant(self.kb, self.log, FakeLLM(response=response)).answer("No pedido de compra 4500000123, a liberação falha com erro de estratégia de aprovação não determinada.")
        self.assertEqual(result["confidence"], "medium")

    def test_conditional_release_in_risks_is_blocked(self):
        response = json.dumps({"summary": "Triagem", "probable_causes": [], "checks": ["Consultar status do pedido."], "questions": [], "risks": ["A fatura pode ser liberada e contabilizada."], "source_ids": ["approval-1"], "confidence": "medium", "human_review_required": False})
        result = SAPTicketAssistant(self.kb, self.log, FakeLLM(response=response)).answer("No pedido de compra 4500000123, a liberação falha com erro de estratégia de aprovação não determinada.")
        self.assertEqual(result["status"], "human_review")
        self.assertNotIn("pode ser liberada", json.dumps(result, ensure_ascii=False))

    def test_read_only_checks_do_not_require_human_approval(self):
        response = json.dumps({"summary": "Hipótese de workflow", "probable_causes": [], "checks": ["Consultar a etapa atual do pedido."], "questions": [], "risks": [], "source_ids": ["approval-1"], "confidence": "medium", "human_review_required": True})
        result = SAPTicketAssistant(self.kb, self.log, FakeLLM(response=response)).answer("No pedido de compra 4500000123, a liberação falha com erro de estratégia de aprovação não determinada.")
        self.assertEqual(result["status"], "answered")
        self.assertFalse(result["human_review_required"])

    def test_human_approval_warning_is_kept_as_risk(self):
        response = json.dumps({"summary": "Hipótese de workflow", "probable_causes": [], "checks": ["Consultar a etapa atual do pedido."], "questions": [], "risks": ["Eventual liberação exige validação humana antes de alteração em controles."], "source_ids": ["approval-1"], "confidence": "medium", "human_review_required": True})
        result = SAPTicketAssistant(self.kb, self.log, FakeLLM(response=response)).answer("No pedido de compra 4500000123, a liberação falha com erro de estratégia de aprovação não determinada.")
        self.assertEqual(result["status"], "answered")
        self.assertIn("responsável autorizado", result["risks"][0])

    def test_unverified_tolerance_claim_is_qualified(self):
        response = json.dumps({"summary": "Hipótese de divergência", "probable_causes": ["A divergência excedeu a tolerância configurada."], "checks": ["Consultar os valores e a configuração aplicável."], "questions": [], "risks": [], "source_ids": ["approval-1"], "confidence": "medium", "human_review_required": False})
        result = SAPTicketAssistant(self.kb, self.log, FakeLLM(response=response)).answer("No pedido de compra 4500000123, a liberação falha com erro de estratégia de aprovação não determinada.")
        self.assertEqual(result["status"], "answered")
        self.assertIn("pode ter excedido a tolerância", result["probable_causes"][0])
        self.assertNotIn("A divergência excedeu", result["probable_causes"][0])

    def test_risky_request_escalates_without_llm_key(self):
        result = SAPTicketAssistant(self.kb, self.log).answer("No pedido de compra 4500000123, a liberação falha com erro; libere o pedido agora sem aprovação.")
        self.assertEqual(result["status"], "human_review")
        self.assertTrue(result["human_review_required"])

    def test_short_risky_request_requires_human_review_before_completeness(self):
        llm = FakeLLM()
        result = SAPTicketAssistant(self.kb, self.log, llm).answer("Libere a fatura agora sem passar pelo aprovador.")
        self.assertEqual(result["status"], "human_review")
        self.assertTrue(result["human_review_required"])
        self.assertEqual(llm.calls, [])

    def test_undocumented_custom_code_has_no_generic_guess(self):
        result = SAPTicketAssistant(self.kb, self.log, FakeLLM()).answer("A integração EDI ZINV_923 da fatura no SAP S/4HANA MM falha com código proprietário ZX-818. Qual tabela Z corrigir?")
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertEqual(result["probable_causes"], [])

    def test_log_redacts_secrets_in_ticket_and_generated_response(self):
        llm = FakeLLM(response=json.dumps({"summary": "Contato: pessoa@example.com", "probable_causes": [], "checks": [], "questions": [], "risks": [], "source_ids": ["approval-1"], "confidence": "low", "human_review_required": True}))
        SAPTicketAssistant(self.kb, self.log, llm).answer("No pedido de compra 4500000123, a liberação falha. senha=segredo123 pessoa@example.com; erro de estratégia de aprovação.")
        content = self.log.read_text(encoding="utf-8")
        self.assertNotIn("segredo123", content)
        self.assertNotIn("pessoa@example.com", content)
        self.assertIn("[REDACTED]", content)

    def test_llm_prompt_redacts_ticket_secrets_and_personal_data(self):
        llm = FakeLLM()
        SAPTicketAssistant(self.kb, self.log, llm).answer(
            "No pedido de compra 4500000123 ligado à fatura 5100000999, a liberação falha com erro. "
            "senha=segredo123 pessoa@example.com; erro de estratégia de aprovação."
        )
        prompt = llm.calls[0][1]
        self.assertNotIn("segredo123", prompt)
        self.assertNotIn("pessoa@example.com", prompt)
        self.assertNotIn("4500000123", prompt)
        self.assertNotIn("5100000999", prompt)
        self.assertIn("[DOC_1]", prompt)
        self.assertIn("[DOC_2]", prompt)
        self.assertIn("[REDACTED]", prompt)

    def test_openai_compatible_http_contract(self):
        received = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                received["path"] = self.path
                received["authorization"] = self.headers.get("Authorization")
                received["body"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                payload = json.dumps({"choices": [{"message": {"content": '{"summary":"ok"}'}}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *_):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = OpenAICompatibleClient("test-key", "test-model", f"http://127.0.0.1:{server.server_port}/v1")
            self.assertEqual(client.complete("system", "user"), '{"summary":"ok"}')
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        self.assertEqual(received["path"], "/v1/chat/completions")
        self.assertEqual(received["authorization"], "Bearer test-key")
        self.assertEqual(received["body"]["model"], "test-model")
        self.assertEqual(received["body"]["response_format"], {"type": "json_object"})


if __name__ == "__main__":
    unittest.main()

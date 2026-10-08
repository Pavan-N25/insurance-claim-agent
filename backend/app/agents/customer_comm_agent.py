from typing import Dict, Any, List
from backend.app.agents.base import BaseAgent
from backend.app.services.notification_service import NotificationService

class CustomerCommunicationAgent(BaseAgent):
    def __init__(self):
        super().__init__("CustomerCommunicationAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Generating customer communications across supported languages...")
        claim_id = state.get("claim_id", "")
        claim_data = state.get("claim_data", {})
        decision = state.get("decision_output", {})
        intake = state.get("intake_output", {})

        status = decision.get("recommendation", "SUBMITTED")
        claimant = claim_data.get("claimant_name", "Valued Customer")
        missing = intake.get("missing_information", [])

        messages = {}
        for lang in ["en", "hi", "kn"]:
            messages[lang] = NotificationService.generate_customer_communication(
                status=status,
                claim_id=claim_id,
                claimant_name=claimant,
                missing_docs=missing,
                language=lang
            )

        return {"customer_messages": messages}

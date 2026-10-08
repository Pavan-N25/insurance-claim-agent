import asyncio
import logging
from typing import Dict, Any, Callable, Optional

from backend.app.agents.intake_agent import IntakeAgent
from backend.app.agents.document_agent import DocumentIntelligenceAgent
from backend.app.agents.vision_agent import VisionDamageAgent
from backend.app.agents.understanding_agent import ClaimUnderstandingAgent
from backend.app.agents.policy_rag_agent import PolicyCoverageAgent
from backend.app.agents.fraud_agent import FraudDetectionAgent
from backend.app.agents.severity_agent import ClaimSeverityAgent
from backend.app.agents.estimation_agent import ClaimEstimationAgent
from backend.app.agents.decision_agent import DecisionAgent
from backend.app.agents.explainability_agent import ExplainabilityAgent
from backend.app.agents.customer_comm_agent import CustomerCommunicationAgent

logger = logging.getLogger("ClaimWorkflowOrchestrator")

class ClaimWorkflowOrchestrator:
    def __init__(self):
        self.intake_agent = IntakeAgent()
        self.document_agent = DocumentIntelligenceAgent()
        self.understanding_agent = ClaimUnderstandingAgent()
        self.vision_agent = VisionDamageAgent()
        self.policy_agent = PolicyCoverageAgent()
        self.fraud_agent = FraudDetectionAgent()
        self.severity_agent = ClaimSeverityAgent()
        self.estimation_agent = ClaimEstimationAgent()
        self.decision_agent = DecisionAgent()
        self.explainability_agent = ExplainabilityAgent()
        self.customer_comm_agent = CustomerCommunicationAgent()

    async def run(
        self,
        state: Dict[str, Any],
        progress_callback: Optional[Callable[[str, int, str], Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes the full multi-agent triage workflow with live milestone streaming.
        """
        async def report_progress(step: str, pct: int, message: str):
            logger.info(f"[{state.get('claim_id')}] Step: {step} ({pct}%) - {message}")
            if progress_callback:
                if asyncio.iscoroutinefunction(progress_callback):
                    await progress_callback(step, pct, message)
                else:
                    progress_callback(step, pct, message)

        try:
            # 1. Intake Agent
            await report_progress("INTAKE", 10, "Validating submission and identifying modalities...")
            state["intake_output"] = await self.intake_agent.process(state)

            # 2. Document Intelligence Agent
            await report_progress("DOCUMENT_AI", 25, "Performing OCR and extracting document tables...")
            state["document_output"] = await self.document_agent.process(state)

            # 3. Claim Understanding Agent
            await report_progress("UNDERSTANDING", 35, "Synthesizing normalized claim representation...")
            state["understanding_output"] = await self.understanding_agent.process(state)

            # 4. Concurrent execution: Vision Damage Assessment & Policy Coverage RAG
            await report_progress("ANALYSIS", 50, "Executing Computer Vision defect detection and Policy RAG...")
            vision_task = self.vision_agent.process(state)
            policy_task = self.policy_agent.process(state)
            vision_res, policy_res = await asyncio.gather(vision_task, policy_task)
            state["vision_output"] = vision_res
            state["policy_output"] = policy_res

            # 5. Fraud Detection Agent
            await report_progress("FRAUD_ANALYSIS", 65, "Scanning perceptual image hashes and entity clusters...")
            state["fraud_output"] = await self.fraud_agent.process(state)

            # 6. Severity Agent
            await report_progress("SEVERITY", 75, "Calculating damage, financial risk, and priority score...")
            state["severity_output"] = await self.severity_agent.process(state)

            # 7. Claim Estimation Agent
            await report_progress("ESTIMATION", 82, "Computing parts, labor, and depreciation payout range...")
            state["estimation_output"] = await self.estimation_agent.process(state)

            # 8. Decision Agent
            await report_progress("DECISION", 90, "Applying safety guardrails and policy triage rules...")
            state["decision_output"] = await self.decision_agent.process(state)

            # 9. Explainability Agent
            await report_progress("EXPLAINABILITY", 95, "Generating plain-English audit explanation and citations...")
            state["explainability_output"] = await self.explainability_agent.process(state)

            # 10. Customer Communication Agent
            await report_progress("NOTIFICATION", 98, "Composing multilingual notifications (EN, HI, KN)...")
            state["customer_comm_output"] = await self.customer_comm_agent.process(state)

            await report_progress("COMPLETED", 100, "Claim triage completed successfully.")
            return state

        except Exception as e:
            logger.error(f"Error in claim workflow: {e}", exc_info=True)
            await report_progress("ERROR", 100, f"Error in claim workflow: {str(e)}")
            raise e

orchestrator = ClaimWorkflowOrchestrator()

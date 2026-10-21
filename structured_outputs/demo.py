from typing import Literal

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from llm_engineering.llm_provider import create_model # pragma: no cover - supports running from repo root


class TicketTriage(BaseModel):
    category: Literal["billing", "technical", "account_access", "other"] = Field(
        description="The main category of the customer's request."
    )
    priority: Literal["low", "normal", "high", "urgent"] = Field(
        description="How quickly the support team should respond."
    )
    summary: str = Field(description="A short summary of the issue.")
    suggested_reply: str = Field(
        description="A brief, helpful reply that does not claim the issue is fixed."
    )


def triage_ticket(ticket: str) -> TicketTriage:
    parser = PydanticOutputParser(pydantic_object=TicketTriage)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You classify support tickets into exactly one category. "
                "Use 'billing' only for charges, refunds, invoices, subscriptions, or payment problems. "
                "Use 'account_access' only for login, password, MFA, locked account, permissions, or access issues. "
                "Use 'technical' only for actual product bugs, crashes, errors, broken features, performance problems, or API failures. "
                "Use 'other' when the ticket is vague, mixed, or does not clearly fit the categories above. "
                "Do not default to 'technical' for billing or access problems. "
                "Do not invent account details, claim an issue is fixed, or include information absent from the ticket.",
            ),
            (
                "human",
                "Classify this support ticket and suggest a brief reply.\n\n"
                "Ticket:\n{ticket}\n\n{format_instructions}",
            ),
        ]
    )
    chain = prompt | create_model() | parser
    return chain.invoke(
        {
            "ticket": ticket,
            "format_instructions": parser.get_format_instructions(),
        }
    )


def main() -> None:
    ticket = input("Please describe the issue, so I can create a ticket for you: ").strip()
    if not ticket:
        print("A support ticket is required.")
        return

    try:
        result = triage_ticket(ticket)
    except OutputParserException as error:
        print(f"The model response did not match the expected schema: {error}")
        return

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
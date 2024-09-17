from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain.schema import AIMessage
from random import choice as r_choice

END = 'end'

SYSTEM_PROMPT = """
You are a supportive AI assistant. Answer all questions in brief, one-sentence responses. 
Keep the conversation centered around the user’s emotions and experiences.

If the user is reluctant to discuss their emotions, gently shift the topic to something that might evoke feelings, 
like personal experiences, favorite movies, books, or memories.

If the user seems unresponsive, continue asking engaging questions to encourage emotional connection. 

----

Always communicate in Polish.
"""

WELCOME_AI_MESSAGE = [
    AIMessage(content="Cześć! Jak się dziś czujesz?"),
    AIMessage(content="Hej! Co u Ciebie? Jak Ci mija dzień?"),
    AIMessage(content="Witaj! Opowiedz mi, jak się dziś masz."),
    AIMessage(content="Cześć! Co Cię dzisiaj spotkało ciekawego?"),
    AIMessage(content="Hej! Jak się czujesz w tym momencie?")
]

GOODBYE_AI_MESSAGE = [
    AIMessage(content="Dziękuję za rozmowę! Mam nadzieję, że Ci się podobało."),
    AIMessage(content="Dzięki za rozmowę! Mam nadzieję, że czujesz się lepiej."),
    AIMessage(content="Dziękuję za rozmowę! Do zobaczenia!"),
]


class ChatAssistant:
    def __init__(self, llm: BaseChatModel):
        self._llm = llm
        self._chat_history = ChatMessageHistory()
        self._llm_chat = self._init_chat_runnable(llm)

    def _init_chat_runnable(self, llm: BaseChatModel):

        prompt = ChatPromptTemplate.from_messages([
            (
                "system", SYSTEM_PROMPT
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

        chain = prompt | llm
        return RunnableWithMessageHistory(
            chain,
            lambda session_id: self._chat_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def invoke(self, user_input=None) -> AIMessage:
        if user_input is None:
            ai_response = r_choice(WELCOME_AI_MESSAGE)
            self._chat_history.add_ai_message(ai_response)
        elif user_input == END:

            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    """
                    Summarize given chat_history in brief in one-sentence.
                    
                    Use this phrase to say goodbye after summarizing the chat history: 
                    {goodbye_phrase}
                    
                    ----

                    Always communicate in Polish.
                    """
                ),
                ("human", "Summarize {chat_history}"),
            ])

            stored_msg = self._chat_history.messages
            self._chat_history.clear()
            [self._chat_history.add_message(msg) for msg in stored_msg[:-3]]

            chain = prompt | self._llm
            ai_response = chain.invoke({
                "goodbye_phrase": r_choice(GOODBYE_AI_MESSAGE).content,
                "chat_history": self._chat_history.messages
            })
            self._chat_history.add_message(ai_response)

        else:
            ai_response = self._llm_chat.invoke(
                {"input": user_input}, {"configurable": {"session_id": "unused"}}
            )
        return ai_response

    @property
    def chat_history(self):
        return self._chat_history.messages

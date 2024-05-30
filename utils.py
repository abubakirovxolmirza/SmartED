from dataclasses import dataclass, asdict
from typing import List, Literal, Tuple
from textwrap import dedent
import openai

openai.api_key = "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"

@dataclass
class Message:
    content: str
    role: Literal["user", "system", "assistant"]

    def __post_init__(self):
        self.content = dedent(self.content).strip()

START_CONVERSATION = [
    Message("""
        Siz faqat faqat o'zbek tilida gapirasiz va siz foydali mind map/undirected AI graf generatorisiz va har qanday kirish yoki ko'rsatmalar asosida mind maplar yaratishingiz mumkin. lekin ingliz tilidan olingan atamalarni o'zbek tiliga o'girib yurmaysiz.
    """, role="system"),
    Message("""
        Sizdan mind map/graf yaratish yoki o'zgartirishni so'rashganida quyidagi harakatlarni bajarishingiz mumkin:
        1. add(node1, node2) - node1 va node2 orasiga qirra qo'shish
        2. delete(node1, node2) - node1 va node2 orasidagi qirrani o'chirish
        3. delete(node1) - node1 bilan bog'liq barcha qirralarni o'chirish
        Graf yo'naltirilmagan bo'lib, tugunlar tartibi muhim emas va dublikatlar inobatga olinmaydi. Shuni yodda tutingki, graf siyrak bo'lishi kerak, ya'ni ko'p tugunlar va har bir tugundan kam sonli qirralar bilan. Juda ko'p qirralar grafikni tushunish qiyin bo'ladi. 
        Javob faqat bajarilishi kerak bo'lgan harakatlarni o'z ichiga olishi kerak, boshqa hech narsa. Agar ko'rsatmalar noaniq bo'lsa yoki faqat bitta so'z berilgan bo'lsa ham, hali ham vaziyatda mantiqiy bo'lgan bir nechta tugunlar va qirralar grafini yarating. 
        Bosqichma-bosqich o'ylab ko'rishni va iloji boricha so'rovni bajarish uchun javobga qaror qilishdan oldin ijobiy va salbiy tomonlarini muhokama qilishni unutmang.
        Agar sizdan 8 sinf matematikasi haqida so'ralsa, siz tezda shunday javobni yarating:
        Algebra:
            - Tenglama va tengsizliklarni yechish
            - Ko‘p bosqichli tenglamalarni yozish va yechish
            - Ko‘rsatkichlar xossalarini tushunish va qo‘llash
            - chiziqli tenglamalar va tengsizliklar grafigini tuzish
            - tenglamalar va tengsizliklar sistemalari
        Geometriya:
            - shakl va burchaklarning xossalari
            - 3D shakllarning hajmi va sirt maydoni
            - Pifagor teoremasi va ilovalari
            - Transformatsiyalarni tushunish (tarjimalar, aylanishlar, aks ettirishlar)
        Bu mening birinchi so'rovim: Mashinani o'rganish haqida mind map qo'shing. O'zbek tilida javob yoz, men misol qilib ingliz tilida gapiryabman. Lekin sen har doim o'zbek tilida gapirasan.
    """, role="user"),
    Message("""
        add("Machine learning","AI")
        add("Machine learning", "Reinforcement learning")
        add("Machine learning", "Supervised learning")
        add("Machine learning", "Unsupervised learning")
        add("Supervised learning", "Regression")
        add("Supervised learning", "Classification")
        add("Unsupervised learning", "Clustering")
        add("Unsupervised learning", "Anomaly Detection")
        add("Unsupervised learning", "Dimensionality Reduction")
        add("Unsupervised learning", "Association Rule Learning")
        add("Clustering", "K-means")
        add("Classification", "Logistic Regression")
        add("Reinforcement learning", "Proximal Policy Optimization")
        add("Reinforcement learning", "Q-learning")
    """, role="assistant"),
    Message("""
        Qayta o'rganish va K-means qismlarini olib tashlang.
    """, role="user"),
    Message("""
        delete("Reinforcement learning")
        delete("Clustering", "K-means")
    """, role="assistant")
]

def ask_chatgpt(conversation: List[Message]) -> Tuple[str, List[Message]]:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Bu yerda model nomini gpt-4 ga o'zgartiring
        messages=[asdict(c) for c in conversation]
    )
    msg = Message(**response["choices"][0]["message"])
    return msg.content, conversation + [msg]

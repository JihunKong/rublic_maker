import streamlit as st
from openai import OpenAI
import pandas as pd
from io import BytesIO
from fpdf import FPDF

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# 교육과정 데이터
curriculum_standards = {
    "중학교": {
        "듣기·말하기": [
            "[9국01-01] 듣기·말하기의 소통 과정을 이해하고 효과적으로 듣기·말하기를 한다.",
            "[9국01-02] 상대의 감정에 공감하며 적절하게 반응하는 대화를 나눈다.",
            "[9국01-03] 목적에 맞게 타당한 근거를 들어 글을 쓴다.",
            "[9국01-04] 토의에서 의견을 교환하여 합리적으로 문제를 해결한다.",
            "[9국01-05] 목적과 상황에 맞게 절차와 규칙을 지키며 토론한다.",
            "[9국01-06] 청중의 관심과 요구를 고려하여 말한다.",
            "[9국01-07] 여러 사람 앞에서 말할 때 부딪히는 어려움에 효과적으로 대처한다.",
            "[9국01-08] 핵심 정보가 잘 드러나도록 내용을 구성하여 발표한다.",
            "[9국01-09] 설득 전략을 비판적으로 분석하며 듣는다.",
            "[9국01-10] 내용의 타당성을 판단하며 듣는다.",
            "[9국01-11] 매체 자료의 효과를 판단하며 듣는다.",
            "[9국01-12] 언어폭력의 문제점을 인식하고 상대를 배려하며 말하는 태도를 지닌다."
        ],
        "읽기": [
            "[9국02-01] 읽기는 글에 나타난 정보와 독자의 배경지식을 활용하여 문제를 해결하는 과정임을 이해하고 글을 읽는다.",
            "[9국02-02] 읽기 목적이나 글의 특성을 고려하여 글 내용을 요약한다.",
            "[9국02-03] 읽기 목적이나 글의 특성을 고려하여 읽기 방법을 적절하게 활용한다.",
            "[9국02-04] 글에 사용된 다양한 설명 방법을 파악하며 읽는다.",
            "[9국02-05] 글에 사용된 다양한 논증 방법을 파악하며 읽는다.",
            "[9국02-06] 동일한 화제의 글이라도 서로 다른 관점과 형식으로 표현될 수 있음을 이해하고 글을 읽는다.",
            "[9국02-07] 매체에 드러난 다양한 표현 방법과 의도를 평가하며 읽는다.",
            "[9국02-08] 도서관이나 인터넷에서 관련 자료를 찾아 참고하면서 한 편의 글을 읽는다.",
            "[9국02-09] 자신의 읽기 과정을 점검하고 효과적으로 조정하며 읽는다.",
            "[9국02-10] 읽기의 가치와 중요성을 깨닫고 읽기를 생활화하는 태도를 지닌다."
        ],
        "쓰기": [
            "[9국03-01] 쓰기는 주제, 목적, 독자, 매체 등을 고려한 문제 해결 과정임을 이해하고 글을 쓴다.",
            "[9국03-02] 대상의 특성에 맞는 설명 방법을 사용하여 글을 쓴다.",
            "[9국03-03] 관찰, 조사, 실험의 절차와 결과가 드러나게 글을 쓴다.",
            "[9국03-04] 주장하는 내용에 맞게 타당한 근거를 들어 글을 쓴다.",
            "[9국03-05] 자신의 삶과 경험을 바탕으로 하여 독자에게 감동이나 즐거움을 주는 글을 쓴다.",
            "[9국03-06] 다양한 자료에서 내용을 선정하여 통일성을 갖춘 글을 쓴다.",
            "[9국03-07] 생각이나 느낌, 경험을 드러내는 다양한 표현을 활용하여 글을 쓴다.",
            "[9국03-08] 영상이나 인터넷 등의 매체 특성을 고려하여 생각이나 느낌, 경험을 표현한다.",
            "[9국03-09] 고쳐쓰기의 일반 원리를 고려하여 글을 고쳐 쓴다.",
            "[9국03-10] 쓰기 윤리를 지키며 글을 쓰는 태도를 지닌다."
        ],
        "문법": [
            "[9국04-01] 언어의 본질에 대한 이해를 바탕으로 하여 국어생활을 한다.",
            "[9국04-02] 음운의 체계를 알고 그 특성을 이해한다.",
            "[9국04-03] 단어를 정확하게 발음하고 표기한다.",
            "[9국04-04] 품사의 종류를 알고 그 특성을 이해한다.",
            "[9국04-05] 어휘의 체계와 양상을 탐구하고 활용한다.",
            "[9국04-06] 문장의 짜임과 양상을 탐구하고 활용한다.",
            "[9국04-07] 담화의 개념과 특성을 이해한다.",
            "[9국04-08] 한글의 창제 원리를 이해한다.",
            "[9국04-09] 통일 시대의 국어에 관심을 가지는 태도를 지닌다."
        ],
        "문학": [
            "[9국05-01] 문학은 심미적 체험을 바탕으로 한 다양한 소통 활동임을 알고 문학 활동을 한다.",
            "[9국05-02] 비유와 상징의 표현 효과를 바탕으로 작품을 수용하고 생산한다.",
            "[9국05-03] 갈등의 진행과 해결 과정에 유의하며 작품을 감상한다.",
            "[9국05-04] 작품에서 보는 이나 말하는 이의 관점에 주목하여 작품을 이해한다.",
            "[9국05-05] 작품이 창작된 사회·문화적 배경을 바탕으로 작품을 이해한다.",
            "[9국05-06] 과거의 삶이 반영된 작품을 오늘날의 삶에 비추어 감상한다.",
            "[9국05-07] 근거의 차이에 따른 다양한 해석을 비교하며 작품을 감상한다.",
            "[9국05-08] 재구성된 작품을 원작과 비교하고, 변화 양상을 파악하며 감상한다.",
            "[9국05-09] 자신의 가치 있는 경험을 개성적인 발상과 표현으로 형상화한다.",
            "[9국05-10] 인간의 성장을 다룬 작품을 읽으며 삶을 성찰하는 태도를 지닌다."
        ]
    },
    "고등학교": {
        "국어": [
            "[10국01-01] 개인이나 집단에 따라 듣기와 말하기의 방법이 다양함을 이해하고 듣기·말하기 활동을 한다.",
            "[10국01-02] 상황과 대상에 맞게 언어 예절을 갖추어 대화한다.",
            "[10국01-03] 논제에 따라 쟁점별로 논증을 구성하여 토론에 참여한다.",
            "[10국01-04] 협상 절차를 이해하고 서로 합의할 수 있는 방안을 탐색하여 의사 결정을 한다.",
            "[10국01-05] 의사소통 과정을 점검하고 조정하며 듣기·말하기 활동을 한다.",
            "[10국02-01] 읽기는 읽기를 통해 서로 영향을 주고받으며 소통하는 사회적 상호 작용임을 이해하고 글을 읽는다.",
            "[10국02-02] 매체에 드러난 필자의 관점이나 표현 방법의 적절성을 평가하며 읽는다.",
            "[10국02-03] 삶의 문제에 대한 해결 방안이나 필자의 생각에 대한 대안을 찾으며 읽는다.",
            "[10국02-04] 읽기 목적을 고려하여 자신의 읽기 방법을 점검하고 조정하며 읽는다.",
            "[10국02-05] 자신의 진로나 관심사와 관련된 글을 자발적으로 찾아 읽는 태도를 지닌다.",
            "[10국03-01] 쓰기는 의미를 구성하여 소통하는 사회적 상호 작용임을 이해하고 글을 쓴다.",
            "[10국03-02] 주제, 독자에 대한 분석을 바탕으로 타당한 근거를 들어 설득하는 글을 쓴다.",
            "[10국03-03] 탐구 과제를 조사하여 절차와 결과가 체계적으로 드러나게 보고하는 글을 쓴다.",
            "[10국03-04] 쓰기 맥락을 고려하여 쓰기 과정을 점검·조정하며 글을 고쳐 쓴다.",
            "[10국03-05] 글을 쓰는 데 필요한 작문의 윤리를 준수하여 책임감 있게 글을 쓰는 태도를 지닌다.",
            "[10국04-01] 국어가 변화하는 실체임을 이해하고 국어생활을 한다.",
            "[10국04-02] 음운의 변동을 탐구하여 올바르게 발음하고 표기한다.",
            "[10국04-03] 문법 요소의 특성을 탐구하고 상황에 맞게 사용한다.",
            "[10국04-04] 한글 맞춤법의 기본 원리와 내용을 이해한다.",
            "[10국04-05] 국어를 사랑하고 국어 발전에 참여하는 태도를 지닌다.",
            "[10국05-01] 문학 작품은 구성 요소들과 전체가 유기적 관계를 맺고 있는 구조물임을 이해하고 문학 활동을 한다.",
            "[10국05-02] 서정 갈래의 표현상 특징과 효과를 이해하고 작품을 감상한다.",
            "[10국05-03] 서사 갈래의 개별 작품을 서사 갈래의 전체 속에서 이해하며 감상한다.",
            "[10국05-04] 극 갈래의 특성과 역사를 고려하여 작품을 이해하고 감상한다.",
            "[10국05-05] 주체적인 관점에서 작품을 해석하고 평가하며 문학을 생활화하는 태도를 지닌다."
        ],
        "화법과 작문": [
            "[12화작01-01] 지역 방언과 사회 방언의 사용 양상을 탐구한다.",
            "[12화작01-02] 다양한 시각과 방법으로 의사소통 과정을 점검하고 조정한다.",
            "[12화작01-03] 언어 공동체의 담화 관습을 이해하고 교양 있는 언어생활을 한다.",
            "[12화작02-01] 대화 방식에 영향을 미치는 자아를 인식하고 관계 형성에 적절한 방식으로 자기를 표현한다.",
            "[12화작02-02] 갈등 상황에서 자신의 생각, 감정이나 바라는 바를 진솔하게 표현한다.",
            "[12화작02-03] 상대측 입장을 이해하고 존중하며 의견을 교환한다.",
            "[12화작03-01] 가치 있는 정보를 선별하고 조직하여 정보를 전달하는 글을 쓴다.",
            "[12화작03-02] 매체 특성을 고려하여 쟁점에 대해 자신의 견해를 표현하는 글을 쓴다.",
            "[12화작03-03] 탐구 기술을 활용하여 독자의 관심과 요구를 고려한 보고서를 쓴다.",
            "[12화작03-04] 타당한 논거를 수집하고 적절한 설득 전략을 활용하여 설득하는 글을 쓴다.",
            "[12화작03-05] 시사적인 현안이나 쟁점에 대해 자신의 관점을 수립하여 비평하는 글을 쓴다.",
            "[12화작03-06] 현안을 분석하여 쟁점을 파악하고 해결 방안을 탐색하는 토론에 참여한다.",
            "[12화작03-07] 협상 절차에 따라 상호 이익이 되도록 의사 결정을 한다.",
            "[12화작03-08] 시사적인 현안이나 쟁점에 대해 자신의 입장을 조리 있게 발표한다."
        ],
        "독서": [
            "[12독서01-01] 학업과 관련된 학습 목적의 글을 읽으며 겪는 어려움을 해결하기 위한 독서 방법을 제안한다.",
            "[12독서01-02] 동일한 화제의 글이라도 서로 다른 관점과 형식으로 표현됨을 이해하며 읽는다.",
            "[12독서01-03] 한 편의 글 또는 매체의 중심 내용을 정확히 파악한다.",
            "[12독서01-04] 한 편의 글 또는 매체에 드러난 내용이나 관점을 비판적으로 살펴 적절성과 타당성을 평가한다.",
            "[12독서02-01] 글에 드러난 정보의 표면적 의미 외에 글의 내포적 의미를 추론한다.",
            "[12독서02-02] 글의 내용과 자신의 배경지식을 바탕으로 글의 내용을 확장하여 해석한다.",
            "[12독서02-03] 글의 전개 과정에서 발견되는 저자의 숨겨진 의도를 추론하며 읽는다.",
            "[12독서03-01] 인문·예술 분야의 글을 읽으며 제재에 담긴 인문학적 세계관, 예술과 삶의 성찰 등을 비판적으로 이해한다.",
            "[12독서03-02] 사회·문화 분야의 글을 읽으며 제재에 담긴 사회적 요구와 신념, 사회·문화적 현상에 대한 인식 등을 비판적으로 이해한다.",
            "[12독서03-03] 과학·기술 분야의 글을 읽으며 제재에 담긴 지식과 정보의 객관성, 논거의 입증 과정과 타당성 등을 비판적으로 이해한다.",
            "[12독서03-04] 교양을 넓히고 인성을 함양하는 독서의 습관화를 위해 독서 계획을 세우고 실천한다."
        ],
        "문학": [
            "[12문학01-01] 문학이 인간과 세계에 대한 이해를 돕고 삶의 의미를 깨닫게 하는 언어 활동임을 이해한다.",
            "[12문학01-02] 섬세한 읽기를 바탕으로 작품을 다양한 맥락에서 이해하고 감상하며 평가한다.",
            "[12문학01-03] 문학과 인접 분야의 관계를 바탕으로 작품을 이해하고 감상하며 평가한다.",
            "[12문학01-04] 문학의 수용과 생산 활동을 통해 다양한 사회·문화적 가치를 이해하고 평가한다.",
            "[12문학01-05] 문학 활동을 생활화하여 인성을 함양하고 삶의 질을 높인다.",
            "[12문학02-01] 서정 갈래의 표현상 특징과 효과를 이해하고 감상한다.",
            "[12문학02-02] 서사 갈래의 개별 작품을 서사 갈래의 전체 속에서 이해하며 감상한다.",
            "[12문학02-03] 극 갈래의 특성과 역사를 고려하여 작품을 이해하고 감상한다.",
            "[12문학02-04] 교술 갈래의 표현상 특징과 효과를 이해하고 작품을 감상한다.",
            "[12문학02-05] 다양한 매체로 구현된 작품의 창의적 표현 방법과 심미적 가치를 문학적 관점에서 수용하고 소통한다.",
            "[12문학03-01] 한국 문학의 개념과 범위를 이해한다.",
            "[12문학03-02] 대표적인 문학 작품을 통해 한국 문학의 전통과 특질을 파악하고 감상한다.",
            "[12문학03-03] 주요 작품을 중심으로 한국 문학의 갈래별 전개와 구현 양상을 탐구한다.",
            "[12문학03-04] 한국 문학 작품에 반영된 시대 상황을 이해하고 문학과 역사의 상호 영향 관계를 탐구한다.",
            "[12문학03-05] 한국 문학과 외국 문학을 비교해서 읽고 한국 문학의 보편성과 특수성을 파악한다.",
            "[12문학03-06] 지역 문학과 한민족 문학, 전통적 문학과 현대적 문학 등 다양한 양태를 중심으로 한국 문학의 발전상을 탐구한다."
        ],
        "언어와 매체": [
            "[12언매01-01] 언어의 본질과 특성을 탐구하고 이해한다.",
            "[12언매01-02] 음운의 체계와 변동에 대한 이해를 바탕으로 올바르게 발음하고 표기한다.",
            "[12언매01-03] 어휘의 체계와 양상을 이해하고 그것을 활용하여 효과적으로 의사소통한다.",
            "[12언매01-04] 문장의 짜임과 특성을 탐구하고 활용한다.",
            "[12언매01-05] 단어, 문장, 담화의 의미 구성 과정을 이해하고 활용한다.",
            "[12언매01-06] 시대와 지역에 따른 언어의 다양성과 변화를 이해한다.",
            "[12언매01-07] 국어의 어문 규범에 대해 이해한다.",
            "[12언매02-01] 매체의 특성에 따른 의사소통의 특징을 이해한다.",
            "[12언매02-02] 매체 언어가 의미를 구성하는 방식을 이해하고 활용한다.",
            "[12언매02-03] 매체의 유형에 따른 정보의 구성과 유통 방식을 이해하고 주체적으로 이용한다.",
            "[12언매02-04] 매체 언어의 표현 방법과 심미적 가치를 이해하고 향유한다.",
            "[12언매02-05] 매체를 바탕으로 하여 형성되는 문화에 대해 비판적으로 이해하고 주체적으로 향유한다.",
            "[12언매02-06] 매체를 활용하여 의사소통 목적과 상황에 맞게 타당한 근거를 들어 설득하는 글을 쓰거나 발표를 한다.",
            "[12언매02-07] 매체를 활용하여 자신의 경험과 생각을 창의적으로 표현한다.",
            "[12언매02-08] 매체를 활용하여 정보를 수집·분석·평가·선택·조직하여 청자나 독자의 관심과 요구를 고려하여 정보를 재구성한다.",
            "[12언매02-09] 다양한 관점과 가치를 고려하여 매체에서 자신의 주장을 효과적으로 표현한다.",
            "[12언매02-10] 매체의 소통 방식과 표현의 특성을 고려하여 다양한 매체로 효과적으로 정보를 소통한다.",
            "[12언매02-11] 매체를 통한 의사소통과 언어생활의 습관을 성찰한다."
        ]
    }
}


def get_gpt_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 교육 전문가입니다. 사용자가 입력한 정보에 따라 긍정적인 표현을 사용하여 평가 루브릭을 작성합니다."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

def generate_rubric_table(criteria_list):
    rubric_data = {}
    for criteria in criteria_list:
        prompt = f"""
        다음 평가 기준에 대한 서술식 5단계 루브릭을 작성해주세요:
        
        평가 기준: {criteria}
        
        각 항목에 대해 긍정적인 표현을 사용하여 설명하고, 최상, 상, 중, 하, 최하 순으로, 진술을 더 상세하고 길게 작성해주세요.
        """

        rubric_text = get_gpt_response(prompt)
        rubric_data[criteria] = rubric_text.splitlines()

    return rubric_data

def create_pdf(rubric_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for criteria, descriptions in rubric_data.items():
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt=criteria, ln=True, align='C')

        pdf.set_font("Arial", size=12)
        pdf.cell(40, 10, txt="레벨", border=1)
        pdf.cell(150, 10, txt="설명", border=1, ln=True)

        levels = ["최상", "상", "중", "하", "최하"]
        for level, description in zip(levels, descriptions):
            pdf.cell(40, 10, txt=level, border=1)
            pdf.multi_cell(150, 10, txt=description, border=1)

        pdf.ln(10)

    return pdf

def main():
    st.title("루브릭 생성기")

    # 트리 구조 선택기 표시
    school_level = st.selectbox("학교급 선택", list(curriculum_standards.keys()))
    subject = st.selectbox("과목 선택", list(curriculum_standards[school_level].keys()))
    standard = st.selectbox("교육과정 성취기준 선택", curriculum_standards[school_level][subject])

    # 활동 입력
    activity = st.text_area("활동 입력", "예: 설득력 있는 글쓰기")

    # 평가 기준 입력
    st.subheader("평가 기준 입력 (최대 5개)")
    criteria1 = st.text_input("평가 기준 1", "")
    criteria2 = st.text_input("평가 기준 2", "")
    criteria3 = st.text_input("평가 기준 3", "")
    criteria4 = st.text_input("평가 기준 4", "")
    criteria5 = st.text_input("평가 기준 5", "")

    criteria_list = [criteria for criteria in [criteria1, criteria2, criteria3, criteria4, criteria5] if criteria]

    if st.button("루브릭 생성"):
        if len(criteria_list) == 0:
            st.warning("최소한 하나의 평가 기준을 입력해주세요.")
        else:
            rubric_data = generate_rubric_table(criteria_list)
            st.markdown("## 생성된 루브릭")

            for criteria, descriptions in rubric_data.items():
                st.markdown(f"### {criteria}")
                df = pd.DataFrame({
                    "레벨": ["최상", "상", "중", "하", "최하"],
                    "설명": descriptions
                })
                st.table(df)

            pdf = create_pdf(rubric_data)
            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            pdf_buffer.seek(0)

            st.download_button(
                label="PDF 다운로드",
                data=pdf_buffer,
                file_name="rubric.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()

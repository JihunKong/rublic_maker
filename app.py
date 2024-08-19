import streamlit as st
from openai import OpenAI
import json
from io import BytesIO
import re

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# 교육과정 데이터 설정
curriculum_standards = {
    "중학교": {
        "듣기·말하기": [
            "[9국01-01] 듣기·말하기는 의미 공유의 과정임을 이해하고 듣기·말하기 활동을 한다.",
            "[9국01-02] 상대의 감정에 공감하며 적절하게 반응하는 대화를 나눈다.",
            "[9국01-03] 목적에 맞게 질문을 준비하여 면담한다.",
            "[9국01-04] 토의에서 의견을 교환하여 합리적으로 문제를 해결한다.",
            "[9국01-05] 토론에서 타당한 근거를 들어 논박한다.",
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
            "[9국02-02] 독자의 배경지식, 읽기 맥락 등을 활용하여 글의 내용을 예측한다.",
            "[9국02-03] 읽기 목적이나 글의 특성을 고려하여 글 내용을 요약한다.",
            "[9국02-04] 글에 사용된 다양한 설명 방법을 파악하며 읽는다.",
            "[9국02-05] 글에 사용된 다양한 논증 방법을 파악하며 읽는다.",
            "[9국02-06] 동일한 화제를 다룬 여러 글을 읽으며 관점과 형식의 차이를 파악한다.",
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
            "[10국01-04] 협상에서 서로 만족할 만한 대안을 탐색하여 의사 결정을 한다.",
            "[10국01-05] 의사소통 과정을 점검하고 조정하며 듣고 말한다.",
            "[10국01-06]언어 공동체의 담화 관습을 성찰하고 바람직한 의사소통 문화 발전에 기여하는 태도를 지닌다."
            "[10국02-01] 읽기는 읽기를 통해 서로 영향을 주고받으며 소통하는 사회적 상호 작용임을 이해하고 글을 읽는다.",
            "[10국02-02] 매체에 드러난 필자의 관점이나 표현 방법의 적절성을 평가하며 읽는다.",
            "[10국02-03] 삶의 문제에 대한 해결 방안이나 필자의 생각에 대한 대안을 찾으며 읽는다.",
            "[10국02-04] 읽기 목적을 고려하여 자신의 읽기 방법을 점검하고 조정하며 읽는다.",
            "[10국02-05] 자신의 진로나 관심사와 관련된 글을 자발적으로 찾아 읽는 태도를 지닌다.",
            "[10국03-01] 쓰기는 의미를 구성하여 소통하는 사회적 상호 작용임을 이해하고 글을 쓴다.",
            "[10국03-02] 주제, 독자에 대한 분석을 바탕으로 타당한 근거를 들어 설득하는 글을 쓴다.",
            "[10국03-03] 자신의 경험과 성찰을 담아 정서를 표현하는 글을 쓴다.",
            "[10국03-04] 쓰기 맥락을 고려하여 쓰기 과정을 점검·조정하며 글을 고쳐 쓴다.",
            "[10국03-05] 글이 독자와 사회에 끼치는 영향을 고려하여 책임감 있게 글을 쓰는 태도를 지닌다.",
            "[10국04-01] 국어가 변화하는 실체임을 이해하고 국어생활을 한다.",
            "[10국04-02] 음운의 변동을 탐구하여 올바르게 발음하고 표기한다.",
            "[10국04-03] 문법 요소의 특성을 탐구하고 상황에 맞게 사용한다.",
            "[10국04-04] 한글 맞춤법의 기본 원리와 내용을 이해한다.",
            "[10국04-05] 국어를 사랑하고 국어 발전에 참여하는 태도를 지닌다.",
            "[10국05-01] 문학 작품은 구성 요소들과 전체가 유기적 관계를 맺고 있는 구조물임을 이해하고 문학 활동을 한다.",
            "[10국05-02] 갈래의 특성에 따른 형상화 방법을 중심으로 작품을 감상한다.",
            "[10국05-03] 문학사의 흐름을 고려하여 대표적인 한국 문학 작품을 감상한다.",
            "[10국05-04] 문학의 수용과 생산 활동을 통해 다양한 사회·문화적 가치를 이해하고 평가한다.",
            "[10국05-05] 주체적인 관점에서 작품을 해석하고 평가하며 문학을 생활화하는 태도를 지닌다."
        ],
        "화법과 작문": [
            "[12화작01-01] 사회적 의사소통 행위로서 화법과 작문의 특성을 이해한다.",
            "[12화작01-02] 화법과 작문 활동이 자아 성장과 공동체 발전에 기여함을 이해한다.",
            "[12화작01-03] 화법과 작문 활동에서 맥락을 고려하는 일이 중요함을 이해한다.",
            "[12화작02-01] 대화 방식에 영향을 미치는 자아를 인식하고 관계 형성에 적절한 방식으로 자기를 표현한다.",
            "[12화작02-02] 갈등 상황에서 자신의 생각, 감정이나 바라는 바를 진솔하게 표현한다.",
            "[12화작02-03] 상대측 입론과 반론의 논리적 타당성에 대해 반대 신문하며 토론한다.",
            "[12화작02-04] 협상 절차에 따라 상황에 맞는 전략을 사용하여 문제를 해결한다."
            "[12화작02-05] 면접에서의 답변 전략을 이해하고 질문의 의도를 파악하여 효과적으로 답변한다."
            "[12화작02-06] 청자의 특성에 맞게 내용을 구성하여 발표한다."
            "[12화작02-07] 화자의 공신력을 이해하고 적절한 설득 전략을 사용하여 연설한다."
            "[12화작02-08] 부탁, 요청, 거절, 사과, 감사의 말을 상황에 맞게 효과적으로 한다."
            "[12화작02-09] 상황에 맞는 언어적 ·준언어적 ·비언어적 표현 전략을 사용하여 말한다."
            "[12화작03-01]  가치 있는 정보를 선별하고 조직하여 정보를 전달하는 글을 쓴다.",
            "[12화작03-02] 작문 맥락을 고려하여 자기를 소개하는 글을 쓴다."
            "[12화작03-03] 탐구 과제를 조사하여 절차와 결과가 잘 드러나게 보고하는 글을 쓴다."
            "[12화작03-04] 타당한 논거를 수집하고 적절한 설득 전략을 활용하여 설득하는 글을 쓴다."
            "[12화작03-05] 시사적인 현안이나 쟁점에 대해 자신의 관점을 수립하여 비평하는 글을 쓴다."
            "[12화작03-06] 현안을 분석하여 쟁점을 파악하고 해결 방안을 담은 건의하는 글을 쓴다."
            "[12화작03-07] 작문 맥락을 고려하여 친교의 내용을 표현하는 글을 쓴다."
            "[12화작03-08] 대상에 대한 생각이나 느낌을 바탕으로 하여 정서를 진솔하게 표현하는 글을 쓴다."
            "[12화작03-09] 일상의 체험을 기록하는 습관을 바탕으로 자신의 삶을 성찰하는 글을 쓴다."
            "[12화작04-01] 화법과 작문의 사회적 책임을 인식하고 의사소통 윤리를 준수하는 태도를 지닌다."
            "[12화작04-02] 화법과 작문의 가치를 이해하고 진심을 담아 의사소통하는 태도를 지닌다."
            "[12화작04-03] 언어 공동체의 담화 및 작문 관습을 이해하고, 건전한 화법과 작문의 문화 발전에 기여하는 태도를 지닌다."
        ],
        "독서": [
            "[12독서01-01] 독서의 목적이나 글의 가치 등을 고려하여 좋은 글을 선택하여 읽는다."
            "[12독서01-02] 동일한 화제의 글이라도 서로 다른 관점과 형식으로 표현됨을 이해하고 다양한 글을 주제 통합적으로 읽는다."
            "[12독서02-01] 글에 드러난 정보를 바탕으로 중심 내용, 주제, 글의 구조와 전개 방식 등 사실적 내용을 파악하며 읽는다."
            "[12독서02-02] 글에 드러나지 않은 정보를 예측하여 필자의 의도나 글의 목적, 숨겨진 주제, 생략된 내용을 추론하며 읽는다."
            "[12독서02-03] 글에 드러난 관점이나 내용, 글에 쓰인 표현 방법, 필자의 숨겨진 의도나 사회·문화적 이념을 비판하며 읽는다."
            "[12독서02-04] 글에서 공감하거나 감동적인 부분을 찾고 이를 바탕으로 글이 주는 즐거움과 깨달음을 수용하며 감상적으로 읽는다."
            "[12독서02-05] 글에서 자신과 사회의 문제를 해결하는 방법이나 필자의 생각에 대한 대안을 찾으며 창의적으로 읽는다."
            "[12독서03-01] 인문·예술 분야의 글을 읽으며 제재에 담긴 인문학적 세계관, 예술과 삶의 문제를 대하는 인간의 태도, 인간에 대한 성찰 등을 비판적으로 이해한다."
            "[12독서03-02] 사회·문화 분야의 글을 읽으며 제재에 담긴 사회적 요구와 신념, 사회적 현상의 특성, 역사적 인물과 사건의 사회·문화적 맥락 등을 비판적으로 이해한다."
            "[12독서03-03] 과학·기술 분야의 글을 읽으며 제재에 담긴 지식과 정보의 객관성, 논거의 입증 과정과 타당성, 과학적 원리의 응용과 한계 등을 비판적으로 이해한다."
            "[12독서03-04] 시대의 사회·문화적 특성이 글쓰기의 관습이나 독서 문화에 반영되어 있음을 이해하고 다양한 시대에서 생산된 가치 있는 글을 읽는다."
            "[12독서03-05] 지역의 사회·문화적 특성이 다양한 형식과 내용으로 글에 반영되어 있음을 이해하고 다양한 지역에서 생산된 가치 있는 글을 읽는다."
            "[12독서03-06] 매체의 유형과 특성을 고려하여 글의 수용과 생산 과정을 이해하고 다양한 매체 자료를 주체적이고 비판적으로 읽는다."
            "[12독서04-01] 장기적인 독서 계획을 세워 자발적으로 독서를 실천함으로써 건전한 독서 문화를 형성한다."
            "[12독서04-02] 의미 있는 독서 활동에 참여함으로써 타인과 교류하고 다양한 삶의 방식과 세계관을 이해하는 태도를 지닌다."            
        ],
        "문학": [
            "[12문학01-01] 문학이 인간과 세계에 대한 이해를 돕고, 삶의 의미를 깨닫게 하며, 정서적, 미적으로 삶을 고양함을 이해한다.",
            "[12문학02-02]작품을 작가, 사회·문화적 배경, 상호 텍스트성 등 다양한 맥락에서 이해하고 감상한다."
            "[12문학02-03]문학과 인접 분야의 관계를 바탕으로 작품을 이해하고 감상하며 평가한다."
            "[12문학02-04]작품을 공감적, 비판적, 창의적으로 수용하고 그 결과를 바탕으로 상호 소통한다."
            "[12문학02-05]작품을 읽고 다양한 시각에서 재구성하거나 주체적인 관점에서 창작한다."
            "[12문학02-06]다양한 매체로 구현된 작품의 창의적 표현 방법과 심미적 가치를 문학적 관점에서 수용하고 소통한다."
	    "[12문학03-01]한국 문학의 개념과 범위를 이해한다."
	    "[12문학03-02]대표적인 문학 작품을 통해 한국 문학의 전통과 특질을 파악하고 감상한다."
	    "[12문학03-03]주요 작품을 중심으로 한국 문학의 갈래별 전개와 구현 양상을 탐구하고 감상한다."
	    "[12문학03-04]한국 문학 작품에 반영된 시대 상황을 이해하고 문학과 역사의 상호 영향 관계를 탐구한다."
	    "[12문학03-05]한국 문학과 외국 문학을 비교해서 읽고 한국 문학의 보편성과 특수성을 파악한다."
	    "[12문학03-06]지역 문학과 한민족 문학, 전통적 문학과 현대적 문학 등 다양한 양태를 중심으로 한국 문학의 발전상을 탐구한다."
	    "[12문학04-01]문학을 통하여 자아를 성찰하고 타자를 이해하며 상호 소통하는 태도를 지닌다."
	    "[12문학04-02]문학 활동을 생활화하여 인간다운 삶을 가꾸고 공동체의 문화 발전에 기여하는 태도를 지닌다."
        ],
        "언어와 매체": [
            "[12언매01-01] 인간의 삶과 관련하여 언어의 특성을 이해한다."
            "[12언매01-02] 국어의 특성과 세계 속에서의 국어의 위상을 이해한다."
            "[12언매01-03]의사소통의 매개체로서 매체의 유형과 특성을 이해한다."
            "[12언매01-04]현대 사회의 소통 현상과 관련하여 매체 언어의 특성을 이해한다.
            "[12언매02-01]실제 국어생활을 바탕으로 음운의 체계와 변동에 대해 탐구한다."
            "[12언매02-02]실제 국어생활을 바탕으로 품사에 따른 개별 단어의 특성을 탐구한다."
            "[12언매02-03]단어의 짜임과 가상 과정을 탐구하고 이를 국어생활에 활용한다."
            "[12언매02-04]단어의 의미 관계를 탐구하고 적절한 어휘 사용에 활용한다."
            "[12언매02-05]문장의 짜임에 대해 탐구하고 정확하면서도 상황에 맞는 문장을 사용한다."
            "[12언매02-06]문법 요소들의 개념과 표현 효과를 탐구하고 실제 국어생활에 활용한다."
            "[12언매02-07]담화의 개념과 특성을 탐구하고 적절하고 효과적인 국어생활을 한다."
            "[12언매02-08]시대 변화에 따른 국어 자료의 차이에 대해 살피고 각각의 자료에 나타나는 언어적 특성을 이해한다."
            "[12언매02-09]다양한 사회에서의 국어 자료의 차이를 이해하고 상황에 맞게 국어 자료를 생산한다."
            "[12언매02-10]다양한 갈래에 따른 국어 자료의 특성을 이해하고 적절하게 국어 자료를 생산한다."
            "[12언매02-11]다양한 국어 자료를 통해 국어 규범을 이해하고 정확성, 적절성, 창의성을 갖춘 국어생활을 한다."
        "실용 국어": [
	        "[12실국01-01]의사소통 맥락에 적합한 어휘를 사용한다."
	        "[12실국01-02]국어의 어법에 맞고 의미가 정확한 문장을 사용한다."
	        "[12실국02-01]필요한 정보를 수집하여 핵심 내용을 이해한다."
	        "[12실국02-02]정보에 담긴 의도를 추론하고 내용을 비판적으로 평가한다."
	        "[12실국02-03]정보를 체계적으로 조직하여 대상과 상황에 적합하게 표현한다."
	        "[12실국03-01]타당한 근거를 들어 자신의 주장을 설득력 있게 표현한다."
	        "[12실국03-02]집단의 의사 결정 과정에 참여하여 합리적 방안을 탐색한다."
	        "[12실국03-03]대화와 타협으로 갈등을 조정하여 문제를 협력적으로 해결한다."
	        "[12실국04-01]상대를 배려하는 태도로 언어 예절을 갖추어 대화한다."
	        "[12실국04-02]상대의 감정을 공감적으로 수용하며 자신의 감정을 적절하게 표현한다."
	        "[12실국05-01]자신이 속한 공동체의 의사소통 문화를 이해한다."
	        "[12실국05-02]독서와 글쓰기를 통하여 자기를 성찰하고 교양을 함양한다."
		],
	    "심화 국어": [
		    "[12심국01-01]학업에 필요한 정보를 수집하여 분석한다."
		    "[12심국01-02]대상과 목적을 고려하여 정보를 체계적으로 조직한다."
		    "[12심국01-03]정보를 정확하고 논리적으로 전달한다."
		    "[12심국02-01]타인의 의견을 비판적으로 이해한다."
		    "[12심국02-02]자신의 생각으로 논점을 구성한다."
		    "[12심국02-03]문제 해결에 필요한 방안을 탐색하여 합리적으로 의사 결정한다."
		    "[12심국03-01]언어 예술의 아름다움을 향유한다."
		    "[12심국03-02]자신의 생각과 느낌을 창의적이고 아름답게 표현한다."
		    "[12심국03-03]공동체의 언어문화 발전에 능동적으로 참여하는 태도를 지닌다."
		    "[12심국04-01]쓰기 윤리의 중요성을 인식하고 책임감 있는 태도로 글을 쓴다."
		    "[12심국04-02]협력적이고 비판적인 태도로 문제를 탐구한다."
		    "[12심국04-03]매체 이용과 표현의 윤리를 준수하는 태도를 지닌다."
		],
		"고전 읽기": [
			"[12고전01-01]고전의 특성을 이해하고 고전 읽기의 중요성을 인식한다."
			"[12고전02-01]인문·예술, 사회·문화, 과학·기술, 문학 등 다양한 분야의 고전을 균형 있게 읽는다."
			"[12고전02-02]시대, 지역, 문화 요인을 고려하며 고전에 담긴 지혜와 통찰을 바탕으로 자아와 세계를 이해한다."
			"[12고전02-03]현대 사회의 맥락을 고려하여 고전을 재해석하고 고전의 가치를 주체적으로 평가한다."
			"[12고전02-04]고전을 통해 알게 된 사실과 깨닫게 된 점을 바탕으로 삶의 다양한 문제에 대처할 수 있는 교양을 함양한다."
			"[12고전03-01]국어 고전에 나타난 글쓰기 전략과 표현 방법을 분석하고 그 효과를 평가한다."
			"[12고전03-02]고전을 읽고 공동의 관심사나 현대 사회에 유효한 문제를 중심으로 통합적인 국어 활동을 수행한다."
			"[12고전04-01]고전 읽기의 생활화를 통해 바람직한 삶에 대해 탐구하고 인성을 함양한다."
		]
    }
}


# GPT 응답 가져오기 함수
def get_gpt_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 교육 전문가입니다. 사용자가 입력한 정보에 따라 긍정적인 표현을 사용하여 평가 루브릭을 작성합니다."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

# 루브릭 표 생성 함수
def generate_rubric_table(criteria_list):
    prompt = f"""
    다음 4개의 평가 기준에 대한 루브릭 표를 작성해주세요:
    
    {', '.join(criteria_list)}
    
    루브릭 표는 다음 형식을 따라야 합니다:
    1. 첫 번째 행은 열 제목으로, '평가 기준', '최상', '상', '중', '하', '최하'를 포함해야 합니다.
    2. 그 다음 4개의 행은 각각 하나의 평가 기준에 대한 내용을 포함해야 합니다.
    3. 각 셀에는 해당 평가 기준과 척도에 맞는 상세한 설명을 작성해주세요.
    4. 표는 마크다운 형식으로 작성해주세요.
    5. 각 척도에 대한 설명은 명확하고 구체적이어야 하며, 사용자의 입력을 최대한 반영해야 합니다.
    6. 항목은 완벽히 채워져야 하며, 빈칸이 없어야 합니다.
    """

    response = get_gpt_response(prompt)
    
    # 마크다운 표 부분만 추출 (불필요한 텍스트 제거)
    match = re.search(r"\|.+\|.+\n\|.+\n(.+)", response, re.DOTALL)
    if match:
        return match.group(0).strip()
    else:
        return "표 생성에 실패했습니다."

# 마크다운 표를 JSON으로 변환하는 함수
def parse_markdown_table(markdown_table):
    lines = markdown_table.strip().split('\n')
    headers = [header.strip() for header in re.findall(r'\|(.+?)\|', lines[0])]
    data = []
    for line in lines[2:]:  # Skip the header separator line
        row = [cell.strip() for cell in re.findall(r'\|(.+?)\|', line)]
        if row and len(row) == len(headers):  # Ensure the row matches the headers
            data.append(dict(zip(headers, row)))
    return data

# 평가 기준이 부족할 경우 자동으로 추가하는 함수
def fill_missing_criteria(criteria_list, total_criteria=4):
    if len(criteria_list) < total_criteria:
        missing_count = total_criteria - len(criteria_list)
        st.info(f"입력되지 않은 평가 기준 {missing_count}개는 자동으로 생성됩니다.")
        
        prompt = f"""
        사용자가 입력하지 않은 평가 기준을 자동으로 생성해주세요. 현재 입력된 기준은 다음과 같습니다:
        {', '.join(criteria_list)}
        
        부족한 평가 기준을 채우기 위해, 추가로 {missing_count}개의 평가 기준을 생성해주세요.
        """

        gpt_generated_criteria = get_gpt_response(prompt).splitlines()
        criteria_list.extend([criteria for criteria in gpt_generated_criteria if criteria])

    return criteria_list[:total_criteria]  # Ensure the list is exactly 4 criteria

def main():
    st.title("루브릭 생성기")

    # 트리 구조 선택기 표시
    school_level = st.selectbox("학교급 선택", list(curriculum_standards.keys()))
    subject = st.selectbox("과목 선택", list(curriculum_standards[school_level].keys()))
    standard = st.selectbox("교육과정 성취기준 선택", curriculum_standards[school_level][subject])

    # 활동 입력
    activity = st.text_area("활동 입력", "예: 설득력 있는 글쓰기")

    # 평가 기준 입력
    st.subheader("평가 기준 입력")
    criteria_inputs = [st.text_input(f"평가 기준 {i+1}", "") for i in range(4)]

    criteria_list = [criteria for criteria in criteria_inputs if criteria]

    if st.button("루브릭 생성"):
        if len(criteria_list) == 0:
            st.warning("최소한 하나의 평가 기준을 입력해주세요.")
        else:
            criteria_list = fill_missing_criteria(criteria_list)
            with st.spinner('루브릭을 생성 중입니다...'):
                markdown_table = generate_rubric_table(criteria_list)
            
            st.markdown("## 생성된 루브릭")
            st.markdown(markdown_table)  # 마크다운 표를 올바르게 렌더링

            # 마크다운 테이블을 JSON으로 변환
            rubric_data = parse_markdown_table(markdown_table)

            # JSON 파일로 저장
            json_buffer = BytesIO()
            json_data = json.dumps(rubric_data, ensure_ascii=False, indent=4)
            json_buffer.write(json_data.encode('utf-8'))
            json_buffer.seek(0)

            st.download_button(
                label="JSON 다운로드",
                data=json_buffer,
                file_name="rubric.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()

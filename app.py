import streamlit as st
from openai import OpenAI
import json
from io import BytesIO
import re

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# 교육과정 데이터 설정
curriculum_standards = {
    # (기존의 교육과정 데이터 그대로 사용)
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

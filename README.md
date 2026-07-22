# checklist

날짜별 할 일을 기록하는 작고 단순한 Linux GTK 데스크톱 앱입니다.

## 주요 기능

- 달력에서 날짜를 선택해 체크리스트 작성
- 체크 완료, 취소선, 여러 줄 항목
- 항목 우클릭으로 삭제하거나 다음 날로 이월
- 가운데 마우스 버튼 드래그로 항목 순서 변경
- `Ctrl+Z` / `Ctrl+Shift+Z` 실행 취소·다시 실행
- `Ctrl+X` / `Ctrl+C` / `Ctrl+V` 잘라내기·복사·붙여넣기
- SQLite 자동 저장과 마지막 창 위치 복원
- 번들 Pretendard 글꼴로 컴퓨터마다 동일한 10pt 표시
- 인터넷 연결 없이 사용

## 요구 사항

- Python 3
- GTK 3
- PyGObject (`python3-gi`)

Ubuntu에서는 다음 패키지가 필요합니다.

```bash
sudo apt install python3 python3-gi gir1.2-gtk-3.0
```

## 설치

```bash
git clone https://github.com/kimyina/checklist.git
cd checklist
chmod +x install.sh uninstall.sh run.sh
./install.sh
```

설치 후 앱 메뉴에서 `checklist`를 검색하거나 터미널에서 실행합니다.

```bash
checklist
```

`~/.local/bin`이 `PATH`에 없다면 로그아웃 후 다시 로그인하거나 다음 명령으로 실행할 수 있습니다.

```bash
~/.local/share/checklist-app/run.sh
```

## 설치하지 않고 실행

```bash
./run.sh
```

## 사용법

- 날짜 클릭: 해당 날짜의 체크리스트 열기
- 항목 왼쪽 클릭: 내용 편집
- `Enter`: 새 항목 추가
- `Shift+Enter`: 항목 안에서 줄바꿈
- 항목 우클릭: `내일로 이월`, `삭제`
- 가운데 버튼 드래그: 항목 순서 변경
- `Esc`: 달력으로 돌아가기

## 제거

```bash
./uninstall.sh
```

제거해도 사용자 데이터는 삭제하지 않습니다.

## 데이터 위치

사용자 체크리스트는 다음 위치에 저장됩니다.

```text
~/.local/share/daily-checklist/checklist.db
```

`XDG_DATA_HOME`이 설정되어 있으면 해당 경로를 사용합니다.

## 포함 글꼴

이 앱은 [Pretendard v1.3.9](https://github.com/orioncactus/pretendard)의
Regular 글꼴을 앱 전용으로 불러옵니다. 시스템에 글꼴을 별도로 설치하지 않으며,
앱을 삭제해도 시스템 글꼴 설정에 영향을 주지 않습니다.

Pretendard는 SIL Open Font License 1.1로 배포됩니다. 라이선스 전문은
`assets/fonts/LICENSE.txt`에서 확인할 수 있습니다.

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from typing import List, Dict

class SlackRecipeBot:
    def __init__(self, token: str):
        self.client = WebClient(token=token)
    
    def create_recipe_message(self, 
                            title: str,
                            image_url: str,
                            ingredients: List[str],
                            steps: List[str],
                            cooking_time: int,
                            popular_with: List[str],
                            recipe_url: str) -> Dict:
        """레시피 메시지를 생성합니다"""
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":tada: *새로운 레시피가 출시되었습니다!*\n여러분의 관심과 호응으로 아래 레시피를 공식 출시하게 되었습니다 :sparkles:"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*:bento:요리명*\n*{title}*"
                }
            },
            {
                "type": "image",
                "title": {
                    "type": "plain_text",
                    "text": title
                },
                "image_url": image_url,
                "alt_text": f"{title} 완성 사진"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*:leafy_green:재료*\n✅ 재료\n" + "\n".join([f"• {ingredient}" for ingredient in ingredients])
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*:man-cook:조리법*\n✅ 만드는 법 (조리시간 {cooking_time}분)\n" + 
                            "\n".join([f"{idx+1}. {step}" for idx, step in enumerate(steps)])
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f":hearts: *가장 많은 관심을 보여주신 분들*: {', '.join(popular_with)}"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":point_right: 자세한 레시피와 영상을 보고 싶다면 아래 버튼을 클릭해주세요!"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "레시피 전체보기",
                            "emoji": True
                        },
                        "url": recipe_url,
                        "style": "primary"
                    }
                ]
            }
        ]
        
        # fallback text 생성
        fallback_text = f"""
        새로운 레시피가 출시되었습니다!
        
        요리명: {title}
        
        재료:
        {', '.join(ingredients)}
        
        조리법:
        {' '.join([f"{idx+1}. {step}" for idx, step in enumerate(steps)])}
        """
        
        return {
            "blocks": blocks,
            "text": fallback_text  # fallback text 추가
        }

    def send_recipe(self, channel_id: str, recipe_data: Dict) -> None:
        """레시피를 Slack 채널에 전송합니다"""
        try:
            message = self.create_recipe_message(
                title=recipe_data['title'],
                image_url=recipe_data['image_url'],
                ingredients=recipe_data['ingredients'],
                steps=recipe_data['steps'],
                cooking_time=recipe_data['cooking_time'],
                popular_with=recipe_data['popular_with'],
                recipe_url=recipe_data['recipe_url']
            )
            
            # 토큰이 제대로 설정되어 있는지 확인
            print(f"Using token: {self.client.token[:10]}...")
            
            response = self.client.chat_postMessage(
                channel=channel_id,
                **message  # blocks와 text를 함께 전송
            )
            print(f"메시지 전송 성공: {response['ts']}")
            
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
            print(f"Full error: {e.response}")

# 사용 예시
if __name__ == "__main__":
    # 직접 토큰과 채널 ID를 설정
    SLACK_BOT_TOKEN = "xoxb-4997656156160-7997102205702-DyekH4lzxr4rvWGNChSXVyFA"
    CHANNEL_ID = "C07V95D03PY"
    
    # 토큰이 없는 경우 에러 발생
    if not SLACK_BOT_TOKEN:
        raise ValueError("SLACK_BOT_TOKEN이 설정되지 않았습니다.")
    
    if not CHANNEL_ID:
        raise ValueError("CHANNEL_ID가 설정되지 않았습니다.")
    
    # 레시피 데이터 예시
    recipe_data = {
        "title": "오크베리 아사이볼",
        "image_url": "https://recipe-image-url.com/acai-bowl.jpg",
        "ingredients": [
            "냉동 오크베리 1컵",
            "바나나 1개",
            "그릭 요거트 1컵",
            "우유 1/2컵",
            "땅콩버터 2큰술",
            "그래놀라 1/2컵",
            "치아씨드 약간"
        ],
        "steps": [
            "냉동베리, 바나나, 그릭 요거트, 우유를 핸드블렌더나 믹서기에 갈아주세요.",
            "컵에 갈아준 재료를 반정도 부어주세요.",
            "땅콩버터를 취향에 맞게 넣어주세요.",
            "그 위에 남은 갈아준 재료를 다시 부어주세요.",
            "바나나, 그래놀라, 냉동베리, 치아씨드를 토핑으로 올려주면 완성입니다."
        ],
        "cooking_time": 10,
        "popular_with": ["20대 여성", "30대 여성", "10대 여성"],
        "recipe_url": "https://recipe-url.com/acai-bowl"
    }
    
    # 봇 초기화 및 메시지 전송
    bot = SlackRecipeBot(SLACK_BOT_TOKEN)
    bot.send_recipe(CHANNEL_ID, recipe_data)
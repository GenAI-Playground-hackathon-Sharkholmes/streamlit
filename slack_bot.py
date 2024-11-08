from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import List, Dict

class SlackRecipeBot:
    def __init__(self, token: str):
        self.client = WebClient(token=token)
    
    def create_recipe_message(self, 
                            title: str,
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
                    "text": f"*:bento: 요리명*\n*{title}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*:leafy_green: 재료*\n✅ 재료\n" + "\n".join([f"• {ingredient}" for ingredient in ingredients])
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*:man-cook: 조리법*\n✅ 만드는 법 (조리시간 {cooking_time}분)\n" + 
                            "\n".join([f"{step}" for idx, step in enumerate(steps)])
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
        
        return {
            "blocks": blocks,
            "text": f"새로운 레시피가 출시되었습니다! - {title}"  # fallback text
        }

    def send_recipe(self, channel_id: str, recipe_data: Dict) -> None:
        """레시피를 Slack 채널에 전송합니다"""
        try:
            message = self.create_recipe_message(
                title=recipe_data['title'],
                ingredients=recipe_data['ingredients'],
                steps=recipe_data['steps'],
                cooking_time=recipe_data['cooking_time'],
                popular_with=recipe_data['popular_with'],
                recipe_url=recipe_data['recipe_url']
            )
            
            response = self.client.chat_postMessage(
                channel=channel_id,
                **message
            )
            print(f"메시지 전송 성공: {response['ts']}")
            
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
            raise e

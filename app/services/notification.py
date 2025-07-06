from dataclasses import dataclass
from email.message import EmailMessage

from aiosmtplib import send

from app.schemas import OrderOut, UserOut


@dataclass(kw_only=True, frozen=True, slots=True)
class NotificationService:

    async def send_reg_email(self, user_email: str, user: UserOut):
        print("МЭНЧИК ЧЕ ЗА ДЕЛА")
        subject = "Вы успешно зарегистрировались"
        body = f"Спасибо за регистрацию - {user.name}!"
        await self._send_email(recipient=user_email, subject=subject, body=body)

    async def send_order_email(self, user_email: str, order: OrderOut):
        subject = "Подтверждение заказа"
        body = f"Спасибо за ваш заказ №{order.id}!\n\nДетали заказа: {order}"
        await self._send_email(recipient=user_email, subject=subject, body=body)

    @staticmethod
    async def _send_email(recipient: str, subject: str, body: str):
        admin_email = "xuy@mail.ru"

        message = EmailMessage()
        message["From"] = admin_email
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        try:
            await send(message, hostname="mail_dev", port=1025, start_tls=False)
            print("ЙОУ ОТПРАЛЕНО")
        except Exception as e:
            print(f"Ошибка при отправке письма: {e}")

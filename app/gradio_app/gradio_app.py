import base64
import json
import os

import gradio as gr
import requests

API_AUTH_URL = os.getenv("API_AUTH_URL", "http://web-proxy/auth")
API_USER_URL = os.getenv("API_USER_URL", "http://web-proxy/user")
API_MODEL_URL = os.getenv("API_MODEL_URL", "http://web-proxy/model")
API_ADMIN_URL = os.getenv("API_ADMIN_URL", "http://web-proxy/admin")


def signup(name, email, password):
    payload = {"name": name, "email": email, "password": password}
    resp = requests.post(f"{API_AUTH_URL}/signup", json=payload)
    if resp.ok:
        return "Пользователь успешно создан"
    else:
        return f"Ошибка: {resp.text}"


def signin(email, password):
    data = {"username": email, "password": password}
    resp = requests.post(f"{API_AUTH_URL}/signin", data=data)
    if resp.ok:
        resp_json = resp.json()
        token = resp_json.get("access_token")
        return "Вход выполнен успешно", token
    else:
        return f"Ошибка: {resp.text}", None


def auth_headers(token):
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def top_up(amount_str, token):
    if not token:
        return "Ошибка: пользователь не авторизован"
    try:
        amount = float(amount_str)
        if amount <= 0:
            return "Ошибка: сумма должна быть больше нуля"
    except Exception:
        return "Ошибка: введите корректное число"

    resp = requests.post(
        f"{API_USER_URL}/top-up",
        json={"amount": amount},
        headers=auth_headers(token)
    )
    if resp.ok:
        data = resp.json()
        return (f"{data.get('message', 'Успешно')} "
                f"Текущий баланс: {data.get('new_balance', '-')}")
    else:
        return f"Ошибка: {resp.text}"


def get_balance(token):
    if not token:
        return "Ошибка: пользователь не авторизован"
    resp = requests.get(f"{API_USER_URL}/balance", headers=auth_headers(token))
    if resp.ok:
        balance = resp.json().get("balance")
        return f"Текущий баланс: {balance}"
    else:
        return f"Ошибка: {resp.text}"


def input_data_to_model(model_data, token):
    if not token:
        return "Ошибка: пользователь не авторизован"
    resp = requests.post(
        f"{API_MODEL_URL}/data-input",
        json={"data": model_data},
        headers=auth_headers(token),
    )
    if resp.ok:
        return "Запрос успешно отправлен"
    else:
        return f"Ошибка: {resp.text}"


def get_predict_history(token):
    if not token:
        return "Ошибка: пользователь не авторизован"
    resp = requests.get(f"{API_USER_URL}/history-predict",
                        headers=auth_headers(token))
    if resp.ok:
        history = resp.json()
        if not history:
            return "История предсказаний пуста."
        result_str = ""
        for item in history:
            result_str += f"Ваш запрос: {item.get('data')}\nРезультат:\n"
            films = item.get("result", [])
            for film in films:
                if film.get("Статус запроса") is not None:
                    result_str += film.get("Статус запроса")
                else:
                    result_str += (f" - {film.get('title')} "
                                   f"({film.get('genre')})\n")
            result_str += "\n"
        return result_str
    else:
        return f"Ошибка: {resp.text}"


def get_transactions(token):
    if not token:
        return "Ошибка: не авторизован"
    resp = requests.get(
        f"{API_USER_URL}/history-transaction",
        headers=auth_headers(token)
    )
    if resp.ok:
        history = resp.json()
        if not history:
            return "История предсказаний пуста."
        result_str = ""
        for item in history:
            result_str += (f" - {item.get('timestamp')} "
                           f"{item.get('transaction_type')} "
                           f"({item.get('transaction_amount')})\n")
            result_str += "\n"
        return result_str
    else:
        return f"Ошибка: {resp.text}"


def admin_top_up(user_id, amount, token):
    if not token:
        return "Ошибка: пользователь не авторизован"
    try:
        amount_val = float(amount)
        if amount_val <= 0:
            return "Ошибка: сумма должна быть больше нуля"
    except Exception:
        return "Ошибка: введите корректное число"
    payload = {"target_user_id": user_id, "amount": amount_val}
    resp = requests.post(
        f"{API_ADMIN_URL}/top-up", json=payload, headers=auth_headers(token)
    )
    if resp.ok:
        data = resp.json()
        msg = (data.get("Успешное пополнение", "") +
               f", сумма: {data.get('Сумма', '')}")
        return msg
    else:
        return f"Ошибка: {resp.text}"


def admin_write_off(user_id, amount, token):
    if not token:
        return "Ошибка: не авторизован"
    try:
        amount_val = float(amount)
        if amount_val <= 0:
            return "Ошибка: сумма должна быть больше нуля"
    except Exception:
        return "Ошибка: введите корректное число"
    payload = {"target_user_id": user_id, "amount": amount_val}
    resp = requests.post(
        f"{API_ADMIN_URL}/write-off", json=payload, headers=auth_headers(token)
    )
    if resp.ok:
        data = resp.json()
        msg = (data.get("Успешное списание", "") +
               f", сумма: {data.get('Сумма', '')}")
        return msg
    else:
        return f"Ошибка: {resp.text}"


def admin_show_transactions(user_id, token):
    if not token:
        return "Ошибка: не авторизован"
    if not user_id:
        return "Пользователь не может быть пустой"
    payload = {"target_user_id": user_id}
    resp = requests.post(
        f"{API_ADMIN_URL}/user-transaction",
        json=payload,
        headers=auth_headers(token)
    )
    if resp.ok:
        transactions = resp.json()
        if not transactions:
            return "Транзакции не найдены."
        result_str = ""
        for tx in transactions:
            for k, v in tx.items():
                result_str += f"{k}: {v}\n"
            result_str += "\n"
        return result_str
    else:
        return f"Ошибка: {resp.text}"


def signout():
    return False, "", "user", gr.update(visible=True)


def get_role_from_token(token):
    try:
        payload_part = token.split(".")[1]
        padding = "=" * (-len(payload_part) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_part + padding)
        payload = json.loads(payload_bytes)
        role = payload.get("role", "user")
        return role
    except Exception:
        return "user"


def signin_and_store_token(email, password):
    msg, token = signin(email, password)
    role = get_role_from_token(token) if token else "user"
    logged_in = token is not None
    return msg, logged_in, token or "", role, gr.update(visible=not logged_in)


def token_changed(token):
    if token and token.strip():
        role = get_role_from_token(token)
        logged_in = True
        return logged_in, token, role, gr.update(visible=False)
    else:
        return False, "", "user", gr.update(visible=True)


def toggle_main_interface(logged_in, role):
    if logged_in:
        main_vis = gr.update(visible=True)
        greeting_text = f"Добро пожаловать, ваша роль - {role}!"
        model_tab_vis = gr.update(visible=True)
        admin_tab_vis = gr.update(visible=(role.lower() == "admin"))
        signout_btn_vis = gr.update(visible=True)
        auth_row_vis = gr.update(visible=False)
    else:
        main_vis = gr.update(visible=False)
        greeting_text = ""
        model_tab_vis = gr.update(visible=False)
        admin_tab_vis = gr.update(visible=False)
        signout_btn_vis = gr.update(visible=False)
        auth_row_vis = gr.update(visible=True)
    return (
        main_vis,
        greeting_text,
        model_tab_vis,
        admin_tab_vis,
        signout_btn_vis,
        auth_row_vis,
    )


with gr.Blocks() as start:
    gr.Markdown("# Пользовательский интерфейс")

    with gr.Column(visible=True) as main_page:
        gr.Markdown("## Главная страница")
        gr.Markdown(
            "Добро пожаловать в ML сервис по поиску фильмов."
        )

        gr.Markdown("## Описание")
        gr.Markdown(
            "### Введение\n\n"
            "Представляем ML-сервис для поиска фильмов по описанию! Если вы хотите найти фильм, "
            "исходя из его сюжета или ключевых слов, просто введите текст, и наш сервис предложит вам подходящие варианты.\n\n"
            "### Как это работает?\n\n"
            "1. **Регистрация**: Пользователь создает аккаунт, заполнив форму регистрации с необходимыми данными.\n\n"
            "2. **Вход в систему**: После регистрации пользователь может войти в систему, используя свои учетные данные.\n\n"
            "3. **Пополнение баланса**: Пользователь пополняет свой баланс, чтобы получить доступ к дополнительным функциям сервиса.\n\n"
            "4. **Ввод данных**: Пользователь вводит текстовое описание фильма или ключевые слова.\n\n"
            "5. **Обработка текста**: Применяется TF-IDF для векторизации текста, чтобы преобразовать его в числовой формат, подходящий для анализа.\n\n"
            "6. **Поиск с помощью KNN**: С помощью алгоритма K-ближайших соседей (KNN) по косинусному расстоянию сравниваем векторы введенного описания с векторами фильмов в нашей базе данных.\n\n"
            "7. **Результаты**: Сервис возвращает список фильмов, которые наиболее соответствуют вашему запросу.\n\n"
            "### Преимущества\n\n"
            "- **Простой интерфейс**: Легко использовать — просто введите описание и получите результаты.\n"
            "- **Точные рекомендации**: Алгоритм KNN обеспечивает высокую точность в поиске подходящих фильмов.\n\n"
            "Попробуйте наш сервис и найдите идеальный фильм для просмотра!"
        )

        register_button = gr.Button("Перейти к регистрации и авторизации")

    token_state = gr.Textbox(
        value="",
        visible=False,
        interactive=True,
        label="token_state",
        elem_id="token_state",
    )
    is_logged_in = gr.State(False)
    user_role = gr.State("user")

    with gr.Row(visible=False) as auth_row:
        with gr.Column():
            gr.Markdown("## Регистрация")
            name_signup = gr.Textbox(label="Имя", type="text")
            email_signup = gr.Textbox(label="Email")
            password_signup = gr.Textbox(label="Пароль", type="password")
            signup_btn = gr.Button("Зарегистрироваться")
            signup_output = gr.Textbox(
                label="Информация о регистрации", interactive=False
            )

        with gr.Column():
            gr.Markdown("## Вход")
            email_signin = gr.Textbox(label="Email")
            password_signin = gr.Textbox(label="Пароль", type="password")
            signin_btn = gr.Button("Войти")
            signin_output = gr.Textbox(label="Информация о входе",
                                       interactive=False)

    signout_btn = gr.Button("Выйти", visible=False)

    with gr.Column(visible=False) as main_interface:
        greeting = gr.Markdown()
        gr.Markdown("---")
        with gr.Tabs() as tabs:
            with gr.Tab("Пополнение баланса"):
                amount_input = gr.Textbox(
                    label="Сумма для пополнения", placeholder="Введите сумму"
                )
                topup_btn = gr.Button("Пополнить")
                topup_output = gr.Textbox(label="Результат", interactive=False)
                topup_btn.click(
                    fn=top_up,
                    inputs=[amount_input, token_state],
                    outputs=topup_output
                )

            with gr.Tab("История предсказаний"):
                history_output = gr.Textbox(label="История", interactive=False)
                refresh_history_btn = gr.Button("Обновить историю")
                refresh_history_btn.click(
                    fn=get_predict_history,
                    inputs=token_state,
                    outputs=history_output
                )

            with gr.Tab("Баланс"):
                balance_output = gr.Textbox(label="Баланс", interactive=False)
                refresh_balance_btn = gr.Button("Обновить баланс")
                refresh_balance_btn.click(
                    fn=get_balance,
                    inputs=token_state,
                    outputs=balance_output
                )

            with gr.Tab("Отправить данные модели") as model_tab:
                model_data = gr.Textbox(label="Данные для модели")
                model_send_btn = gr.Button("Отправить")
                model_output = gr.Textbox(label="Информация",
                                          interactive=False)
                model_send_btn.click(
                    fn=input_data_to_model,
                    inputs=[model_data, token_state],
                    outputs=model_output,
                )

            with gr.Tab("История транзакций"):
                history_tr = gr.Textbox(label="Ваша история",
                                        interactive=False)
                history_get_tr = gr.Button("Показать историю")
                history_tr_output = gr.Textbox(label="Информация",
                                               interactive=False)
                history_get_tr.click(
                    fn=get_transactions,
                    inputs=token_state,
                    outputs=history_tr_output
                )

            with gr.Tab("Панель администратора", visible=False) as admin_tab:
                admin_user_id = gr.Textbox(label="ID пользователя")
                admin_amount = gr.Textbox(label="Сумма")
                admin_topup_btn = gr.Button("Пополнить пользователя")
                admin_writeoff_btn = gr.Button("Списать со счета пользователя")
                admin_transactions_btn = gr.Button(
                    "Показать транзакции пользователя"
                )
                admin_output = gr.Textbox(label="Информация",
                                          interactive=False)

                admin_topup_btn.click(
                    fn=admin_top_up,
                    inputs=[admin_user_id, admin_amount, token_state],
                    outputs=admin_output,
                )

                admin_writeoff_btn.click(
                    fn=admin_write_off,
                    inputs=[admin_user_id, admin_amount, token_state],
                    outputs=admin_output,
                )

                admin_transactions_btn.click(
                    fn=admin_show_transactions,
                    inputs=[admin_user_id, token_state],
                    outputs=admin_output,
                )

    signup_btn.click(
        fn=signup,
        inputs=[name_signup, email_signup, password_signup],
        outputs=signup_output,
    )

    signin_btn.click(
        fn=signin_and_store_token,
        inputs=[email_signin, password_signin],
        outputs=[signin_output, is_logged_in, token_state, user_role,
                 auth_row]
    )

    signout_btn.click(
        fn=signout,
        inputs=[],
        outputs=[is_logged_in, token_state, user_role, auth_row]
    )

    token_state.change(
        fn=token_changed,
        inputs=token_state,
        outputs=[is_logged_in, token_state, user_role, auth_row],
    )

    def update_ui(logged_in, role):
        return toggle_main_interface(logged_in, role)

    is_logged_in.change(
        fn=update_ui,
        inputs=[is_logged_in, user_role],
        outputs=[
            main_interface,
            greeting,
            tabs,
            admin_tab,
            signout_btn,
            auth_row],
    )
    user_role.change(
        fn=update_ui,
        inputs=[is_logged_in, user_role],
        outputs=[
            main_interface,
            greeting,
            tabs,
            admin_tab,
            signout_btn,
            auth_row],
    )

    register_button.click(
        lambda: (gr.update(visible=False), gr.update(visible=True)),
        inputs=[],
        outputs=[main_page, auth_row]
    )

if __name__ == "__main__":
    start.launch(server_name="0.0.0.0", server_port=7860)

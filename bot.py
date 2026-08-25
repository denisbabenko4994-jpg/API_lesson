import os
import json
from dotenv import load_dotenv
from yandex_ai_studio_sdk import AIStudio

# Загружаем переменные из .env
# Загружаем переменные из .env
load_dotenv()

# Инициализируем SDK (он сам подтянет YC_API_KEY и YC_FOLDER_ID из .env)
sdk = AIStudio()

print("--- Yandex AI Studio Чат-бот запущен ---")

# Шаг 3: Пользователь вводит вопрос в консоль
user_prompt = input("Задайте вопрос нейросети: ")

# Шаг 4: Системная инструкция
system_instruction = "Отвечай кратко, как эксперт, используй примеры."

# Шаг 6: Настройка параметров (temperature 0.3 или 1.5)
# Создаем модель YandexGPT и настраиваем температуру
model = sdk.models.completions("yandexgpt").configure(
    temperature=0.3
)

# Отправляем запрос с системной инструкцией и вопросом пользователя
response = model.run([
    {"role": "system", "text": system_instruction},
    {"role": "user", "text": user_prompt}
])

print("\n=== Ответ модели ===")
print(response.text)

# Шаг 5: Выводим расход токенов
print("\n=== Расход токенов ===")
if hasattr(response, 'usage') and response.usage:
    print(f"Input tokens: {response.usage.input_text_tokens}")
    print(f"Output tokens: {response.usage.completion_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")

# Шаг 5: Вывод структуры ответа в JSON
print("\n=== Полный ответ (JSON) ===")
response_dict = response.to_dict() if hasattr(response, 'to_dict') else str(response)
print(json.dumps(response_dict, indent=4, ensure_ascii=False))
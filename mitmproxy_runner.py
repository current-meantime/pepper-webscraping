from mitmproxy import http
import json
import time
from config import Config

output_directory = Config().mitm_output_dir

# run in terminal: mitmproxy -s mitmproxy_runner.py
def response(flow: http.HTTPFlow) -> None:
    if "pepper.pl/graphql" in flow.request.url:
        print(f"Przechwycono zapytanie: {flow.request.url}")
        try:
            data = json.loads(flow.response.text)
            timestamp = int(time.time())
            output_file_path = output_directory / f"response_{timestamp}.json"
            with open(output_file_path, 'w', encoding='utf-8') as out:
                json.dump(data, out, ensure_ascii=False, indent=4)
            print(f"Zapisano odpowiedź do {output_file_path}")
        except json.JSONDecodeError:
            print(f"Błąd w dekodowaniu JSON: {flow.response.text[:100]}...")  # Pokazuje pierwsze 100 znaków
        except Exception as e:
            print(f"Wystąpił nieoczekiwany błąd: {str(e)}")

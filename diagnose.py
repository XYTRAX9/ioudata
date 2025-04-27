#!/usr/bin/env python3

import requests
import sys
import json

BASE_URL = "http://localhost:8000/api"
ENDPOINTS = [
    {"method": "OPTIONS", "path": "/auth/token", "data": None},
    {"method": "POST", "path": "/auth/token", "data": {"username": "admin", "password": "admin"}},
    {"method": "POST", "path": "/auth-diagnostic", "data": {"username": "admin", "password": "admin"}}
]

def check_endpoint(method, path, data=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    print(f"\n=== Проверка {method} {url} ===")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if data:
                response = requests.post(url, data=data, headers=headers)
            else:
                response = requests.post(url, headers=headers)
        elif method == "OPTIONS":
            response = requests.options(url)
        else:
            print(f"Неподдерживаемый метод: {method}")
            return
        
        print(f"Статус: {response.status_code}")
        print(f"Заголовки: {response.headers}")
        
        if response.text:
            try:
                pretty_json = json.dumps(response.json(), indent=2, ensure_ascii=False)
                print(f"Тело ответа: {pretty_json}")
            except json.JSONDecodeError:
                print(f"Тело ответа (не JSON): {response.text}")
        else:
            print("Пустое тело ответа")
            
    except requests.RequestException as e:
        print(f"Ошибка запроса: {e}")

def main():
    print("=== Диагностика API ===")
    
    for endpoint in ENDPOINTS:
        check_endpoint(endpoint["method"], endpoint["path"], endpoint["data"])
    
    print("\n=== Диагностика завершена ===")

if __name__ == "__main__":
    main() 
import asyncio
import httpx
import uuid

BASE_URL = "http://localhost:8000/api/v1"

async def test_all_apis():
    print("--- API Testleri Basliyor ---\n")
    
    unique_id = str(uuid.uuid4())[:8]
    email = f"test_{unique_id}@example.com"
    password = "SuperSecretPassword123!"
    
    async with httpx.AsyncClient() as client:
        # 1. Health Kontrolü
        print("1. Health Check Test ediliyor...")
        res = await client.get("http://localhost:8000/health")
        print(f"Status: {res.status_code}")
        print(res.json(), "\n")
        
        # 2. Auth: Register
        print("2. Auth: Register Test ediliyor...")
        register_data = {"username": f"user_{unique_id}", "email": email, "password": password}
        res = await client.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Status: {res.status_code}")
        print(res.json(), "\n")
        
        # 3. Auth: Login
        print("3. Auth: Login Test ediliyor...")
        res = await client.post(f"{BASE_URL}/auth/login", json=register_data)
        print(f"Status: {res.status_code}")
        login_data = res.json()
        print(login_data, "\n")
        
        if res.status_code != 200:
            print("[HATA] Login basarisiz oldugu icin test bitiriliyor.")
            return

        access_token = login_data.get("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 4. Auth: Me
        print("4. Auth: Get Current User Test ediliyor...")
        res = await client.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Status: {res.status_code}")
        print(res.json(), "\n")

        # 5. Projects: Create
        print("5. Projects: Proje Olusturma Test ediliyor...")
        project_data = {"name": f"Test Projesi {unique_id}"}
        res = await client.post(f"{BASE_URL}/projects/", json=project_data, headers=headers)
        print(f"Status: {res.status_code}")
        project_created = res.json()
        print(project_created, "\n")
        
        project_id = None
        if res.status_code == 201 or res.status_code == 200:
             project_id = project_created.get("id")

        if not project_id:
             print("[HATA] Proje olusturmada hata alindi, listeleme geciliyor.")
             return

        # 6. Projects: List
        print("6. Projects: Projeleri Listeleme Test ediliyor...")
        res = await client.get(f"{BASE_URL}/projects/", headers=headers)
        print(f"Status: {res.status_code}")
        print(f"Projeler: {len(res.json())} adet bulundu.", "\n")
        
        # 7. Projects: Get Single Project
        print("7. Projects: Tek Proje Getirme Test ediliyor...")
        res = await client.get(f"{BASE_URL}/projects/{project_id}", headers=headers)
        print(f"Status: {res.status_code}")
        print(res.json(), "\n")

        # 8. Agent: Sessions (Empty)
        print("8. Agent: Session Gecmisini Listeleme Test ediliyor...")
        res = await client.get(f"{BASE_URL}/agent/sessions/{project_id}", headers=headers)
        print(f"Status: {res.status_code}")
        print(res.json(), "\n")
        
        # Sorumluluk reddi: k8s konfigürasyonları ayarlanmadığı için podlar minikube 
        # olmadan tam calısmayabilir. Agent call yapıldığında hata dönebilir.
        print("⚠️ Not: Agent ve GitHub Clone endpoint'leri gerçek K8S (Minikube) veya dış kaynaklara ihtiyaç duyduğundan manuel olarak test edilmelidir.")
        
        print("\n--- Temel API Testleri Tamamlandi ---\n")

if __name__ == "__main__":
    asyncio.run(test_all_apis())

import requests

url = "https://catalogo.datosabiertos.miteco.gob.es/catalogo/api/3/action/package_search"

temas = [
    "Control de Seguimiento del Estado General de las Aguas",
    "Vertederos de Residuos"
]

for tema in temas:
    params = {
        "q": f'"{tema}"',
        "rows": 5
    }

    response = requests.get(url, params=params, verify=False)
    data = response.json()

    print("\n" + "=" * 60)
    print("BUSQUEDA:", tema)
    print("=" * 60)

    for dataset in data["result"]["results"]:
        print("\nDATASET:", dataset["title"])

        for recurso in dataset["resources"]:
            print("  Nombre:", recurso.get("name"))
            print("  Formato:", recurso.get("format"))
            print("  DataStore:", recurso.get("datastore_active"))
            print("  ID:", recurso.get("id"))
            print("  URL:", recurso.get("url"))

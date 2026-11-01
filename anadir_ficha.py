#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Añade una ficha a la lista FICHAS de ciencias_tablet.html.

Uso: poner este archivo en la raíz del proyecto (junto al HTML y la carpeta
"imagenes") y ejecutar:   python anadir_ficha.py
Opcional:                  python anadir_ficha.py otro_archivo.html
"""
import glob, json, os, re, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
MARCA = "const FICHAS=["


def buscar_html():
    if len(sys.argv) > 1:
        return os.path.abspath(sys.argv[1])
    for f in sorted(glob.glob(os.path.join(AQUI, "*.html"))):
        with open(f, encoding="utf-8") as fh:
            if MARCA in fh.read():
                return f
    sys.exit("No encuentro ningún .html con la lista FICHAS en esta carpeta.")


def preguntar(texto, defecto=""):
    r = input(texto + (f" [{defecto}]" if defecto else "") + ": ").strip()
    return r or defecto


def elegir_tema(html):
    temas = re.findall(r'id:"([\w-]+)",icon:"[^"]*",title:"([^"]*)"', html)
    if not temas:
        sys.exit("No encuentro temas en el HTML.")
    print("\nTemas disponibles:")
    for i, (tid, titulo) in enumerate(temas, 1):
        print(f"  {i}. {tid}  ({titulo})")
    while True:
        r = preguntar("Elige el tema (número o id)")
        if r.isdigit() and 1 <= int(r) <= len(temas):
            return temas[int(r) - 1][0]
        if r in [t[0] for t in temas]:
            return r
        print("  No es válido, prueba otra vez.")


def elegir_imagen(html, carpeta):
    libres = []
    if os.path.isdir(carpeta):
        for f in sorted(os.listdir(carpeta)):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")) and f'img:"{f}"' not in html:
                libres.append(f)
    if libres:
        print("\nImágenes de la carpeta que aún no son ficha:")
        for i, f in enumerate(libres, 1):
            print(f"  {i}. {f}")
    else:
        print("\n(No hay imágenes nuevas en la carpeta 'imagenes'.)")
    while True:
        r = preguntar("Nombre del archivo de imagen (o número de la lista)")
        if r.isdigit() and 1 <= int(r) <= len(libres):
            r = libres[int(r) - 1]
        if not r:
            continue
        if f'img:"{r}"' in html:
            print("  Esa imagen ya está añadida como ficha.")
            continue
        if not os.path.isfile(os.path.join(carpeta, r)):
            if preguntar(f"  No veo '{r}' en la carpeta imagenes. ¿Usarla igualmente? (s/n)", "n").lower() != "s":
                continue
        return r


def pedir_palabras():
    print("\nEscribe o pega las palabras separadas por comas (o una por línea).")
    print("Cuando termines, deja una línea vacía y pulsa Enter.")
    texto = []
    while True:
        l = input("> ")
        if not l.strip():
            if texto:
                break
            continue
        texto.append(l)
    palabras = [p.strip() for p in re.split(r"[,;\n]", "\n".join(texto)) if p.strip()]
    return palabras


def main():
    ruta = buscar_html()
    with open(ruta, encoding="utf-8") as fh:
        html = fh.read()
    print("Archivo:", ruta)
    tema = elegir_tema(html)
    img = elegir_imagen(html, os.path.join(os.path.dirname(ruta), "imagenes"))
    base = os.path.splitext(img)[0].replace("_", " ")
    en = preguntar("\nTítulo en inglés", base)
    es = preguntar("Título en español", en)
    palabras = pedir_palabras()

    linea = "{t:%s,img:%s,title:[%s,%s],w:[%s]}" % (
        json.dumps(tema), json.dumps(img, ensure_ascii=False),
        json.dumps(en, ensure_ascii=False), json.dumps(es, ensure_ascii=False),
        ",".join(json.dumps(p, ensure_ascii=False) for p in palabras))

    ini = html.index(MARCA) + len(MARCA)
    fin = html.index("\n];", ini)
    bloque = html[ini:fin].rstrip()
    if bloque.strip() and not bloque.endswith(","):
        bloque += ","
    nuevo = html[:ini] + bloque + "\n" + linea + html[fin:]

    print("\nSe añadirá esta línea:\n  " + linea)
    if preguntar("¿Guardar? (s/n)", "s").lower() != "s":
        sys.exit("Cancelado, no se ha cambiado nada.")
    shutil.copyfile(ruta, ruta + ".bak")
    with open(ruta, "w", encoding="utf-8", newline="") as fh:
        fh.write(nuevo)
    print(f"\n✅ Ficha añadida. Copia de seguridad: {os.path.basename(ruta)}.bak")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelado.")

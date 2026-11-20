#!/usr/bin/env python3
"""Gera site/publicar/site.html: cópia do site com as fotos servidas pela CDN jsDelivr (a partir do GitHub).
Usado pela publicação na Vercel, que carrega esta cópia. Uso: python3 site/publicar/gerar.py <commit>"""
import os
import sys

sha = sys.argv[1]
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = f"https://cdn.jsdelivr.net/gh/joaovitornetti2-web/mesa3d@{sha}/site/img/"
s = open(os.path.join(raiz, "index.html"), encoding="utf-8").read()
s = s.replace('src="img/', 'src="' + base).replace("`img/", "`" + base)
open(os.path.join(raiz, "publicar", "site.html"), "w", encoding="utf-8").write(s)
print("ok", base)

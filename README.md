# Lexicon Studio Web - Despliegue Múltiples Plataformas GRATUITAS

## 🎉 ¡App Completa y Lista para Hosting!

**Lexicon Studio Web** es **100% estática** (HTML/CSS/JS + localStorage). Funciona offline, móvil/PC responsiva:
- ✅ Gestión palabras: CRUD, búsqueda, categorías, links RAE/Wiki
- ✅ Juego Ahorcado: Canvas animado, teclado touch
- ✅ Stats dashboard
- ✅ Datos persistentes en navegador

**Desktop**: Corre lexicon.exe (build/)
**Backend opcional**: Supabase (supabase_functions.sql)

## 🚀 DESPLIEGUE GRATUITO - GitHub Pages (Recomendado)

1. **Crea repo en GitHub**:
   - github.com → New Repository → `LexiconWeb`

2. **Desde terminal VSCode** (en c:/Piton/LexiconWeb):
   ```
   git init
   git add .
   git commit -m "LexiconWeb v1.0 - Web + Desktop"
   git branch -M main
   git remote add origin https://github.com/TUUSUARIO/LexiconWeb.git
   git push -u origin main
   ```

3. **Deploy Web en GitHub Pages**:
   - Repo → Settings → Pages → Source: Deploy from branch `main` `/ (root)`
   - **URL lista en 2 min**: `https://TUUSUARIO.github.io/LexiconWeb/`

4. **Sube .exe**:
   - Releases → Draft new release → Sube `build/lexicon/lexicon.exe`

**¡Web live + descarga .exe gratis forever!**

## 📁 Despliegue cPanel (Alternativa)

```
zip -r LexiconWeb.zip index.html style.css script.js words.json README.md TODO.md -x "*.py" "*.pyc" "build/*"
```
- cPanel → File Manager → public_html/ → Upload & Extract
- Accede: `tudominio.com/index.html`

## 🧪 Test Local
```
npx serve .    # o
python -m http.server 8000
```
Abrir `localhost:8000/8000`

## 🔧 Plataformas Adicionales GRATUITAS
| Plataforma | Tipo | Comando/Enlace |
|------------|------|----------------|
| **Netlify** | Web estática | [netlify.com/drop](https://app.netlify.com/drop) (arrastra carpeta) |
| **Render** | Python + Web | render.com → New Static Site |
| **Vercel** | Web | vercel.com → Import Git |
| **Itch.io** | .exe juego | itch.io → Upload lexicon.exe |
| **PythonAnywhere** | Python web | pythonanywhere.com (main.py → web2py) |

## 📱 Funciona en
- Chrome/Firefox/Safari (móvil/PC)
- **Offline** (localStorage persiste datos)

## 📈 Próximos Pasos (TODO.md)
- Backend Supabase full (ya tienes SQL)
- PWA installable
- Modo oscuro
- Multi-idioma

**¡Sube a GitHub ya!** Comparte `github.io` link. © 2024 Lexicon Studio v1.0

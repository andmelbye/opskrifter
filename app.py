import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

CATEGORIES = [
    "🥗 Vegetarian",
    "🌱 Vegan",
    "🍝 Pasta",
    "🐔 Chicken",
    "🥩 Beef",
    "🐷 Pork",
    "🐟 Fish & Seafood",
    "🍜 Soup",
    "🥚 Eggs",
    "🧆 Tofu",
    "🍕 Pizza",
    "🌮 Mexican",
    "🍛 Asian",
    "🥘 Mediterranean",
    "🍰 Dessert",
    "🥞 Breakfast",
    "🥙 Salad",
    "🍞 Bread & Baking",
]

FIELDS = ["title","description","image_url","source_url","servings",
          "prep_time","cook_time","rating","categories","tags",
          "ingredients","instructions","notes"]

# ── Google Sheets connection ──────────────────────────────────
@st.cache_resource
def get_sheet():
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
    )
    client = gspread.authorize(creds)
    sheet = client.open(st.secrets["SHEET_NAME"]).sheet1
    # Write header row if sheet is empty
    if not sheet.row_values(1):
        sheet.append_row(FIELDS)
    return sheet

def load_recipes():
    sheet = get_sheet()
    rows = sheet.get_all_records()
    recipes = []
    for row in rows:
        r = dict(row)
        # Parse categories and tags back from stored strings
        r["categories"] = [c for c in r.get("categories","").split("||") if c]
        recipes.append(r)
    return recipes

def save_new_recipe(data):
    sheet = get_sheet()
    cats = "||".join(data.get("categories", []))
    row = [
        data.get("title",""),
        data.get("description",""),
        data.get("image_url",""),
        data.get("source_url",""),
        data.get("servings",""),
        data.get("prep_time",""),
        data.get("cook_time",""),
        data.get("rating", 5),
        cats,
        data.get("tags",""),
        data.get("ingredients",""),
        data.get("instructions",""),
        data.get("notes",""),
    ]
    sheet.append_row(row)

def update_recipe(row_number, data):
    """row_number is 1-indexed sheet row (add 2: 1 for header, 1 for 1-index)"""
    sheet = get_sheet()
    cats = "||".join(data.get("categories", []))
    row = [
        data.get("title",""),
        data.get("description",""),
        data.get("image_url",""),
        data.get("source_url",""),
        data.get("servings",""),
        data.get("prep_time",""),
        data.get("cook_time",""),
        data.get("rating", 5),
        cats,
        data.get("tags",""),
        data.get("ingredients",""),
        data.get("instructions",""),
        data.get("notes",""),
    ]
    sheet_row = row_number + 2  # +1 for header, +1 for 1-indexing
    sheet.update(f"A{sheet_row}:{chr(65+len(FIELDS)-1)}{sheet_row}", [row])

def delete_recipe(row_number):
    sheet = get_sheet()
    sheet_row = row_number + 2
    sheet.delete_rows(sheet_row)
    st.cache_resource.clear()
    st.rerun()

def recipe_form(existing=None):
    e = existing or {}
    st.subheader("Basic info")
    title = st.text_input("Recipe title *", value=e.get("title",""), placeholder="e.g. Pasta Carbonara")
    description = st.text_area("Short description", value=e.get("description",""), placeholder="A quick one-liner about the dish", height=70)
    image_url = st.text_input("Image URL", value=e.get("image_url",""), placeholder="Paste an image link from Imgur, Google Photos, etc.")
    source_url = st.text_input("Source / recipe link", value=e.get("source_url",""), placeholder="Link to the original recipe (optional)")

    col1, col2, col3 = st.columns(3)
    with col1:
        servings = st.text_input("Servings", value=e.get("servings",""), placeholder="e.g. 4")
    with col2:
        prep_time = st.text_input("Prep time", value=e.get("prep_time",""), placeholder="e.g. 15 min")
    with col3:
        cook_time = st.text_input("Cook time", value=e.get("cook_time",""), placeholder="e.g. 30 min")

    rating = st.select_slider("Rating", options=[1,2,3,4,5], value=int(e.get("rating", 5)))

    st.subheader("Categories")
    existing_cats = e.get("categories", [])
    categories = st.multiselect("Select all that apply", options=CATEGORIES,
                                default=[c for c in existing_cats if c in CATEGORIES])
    tags = st.text_input("Extra tags (comma separated)", value=e.get("tags",""),
                         placeholder="e.g. quick, date night, summer")

    st.subheader("Recipe details")
    st.caption("You can use markdown: **bold**, _italic_, - bullet lists, 1. numbered lists")
    ingredients = st.text_area("Ingredients", value=e.get("ingredients",""),
                               placeholder="- 200g spaghetti\n- 2 eggs\n- 100g pancetta", height=150)
    instructions = st.text_area("Instructions", value=e.get("instructions",""),
                                placeholder="1. Boil pasta...\n2. Fry pancetta...", height=200)
    notes = st.text_area("Notes / tips", value=e.get("notes",""),
                         placeholder="Any extra tips, substitutions, or variations", height=80)

    return dict(title=title, description=description, image_url=image_url,
                source_url=source_url, servings=servings, prep_time=prep_time,
                cook_time=cook_time, rating=rating, categories=categories,
                tags=tags, ingredients=ingredients, instructions=instructions, notes=notes)

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Our Recipe Book", page_icon="🍽️", layout="wide")
st.markdown("""
<style>
    .tag { display:inline-block; background:#fff3e0; color:#e65100; border-radius:20px;
           padding:2px 10px; font-size:0.75rem; margin-right:4px; margin-bottom:2px; }
    .category-badge { display:inline-block; background:#e8f5e9; color:#2e7d32;
                      border-radius:20px; padding:2px 10px; font-size:0.75rem;
                      margin-right:4px; margin-bottom:2px; }
    .rating { color:#f5a623; font-size:1.1rem; }
    h1 { font-size:2rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
for key, default in [("page","home"), ("selected_recipe",None), ("selected_index",None)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── DETAIL PAGE ───────────────────────────────────────────────
if st.session_state.page == "detail":
    recipe = st.session_state.selected_recipe
    idx = st.session_state.selected_index

    back_col, edit_col = st.columns([5,1])
    with back_col:
        if st.button("← Back to all recipes"):
            st.session_state.page = "home"
            st.rerun()
    with edit_col:
        if st.button("✏️ Edit", use_container_width=True):
            st.session_state.page = "edit"
            st.rerun()

    st.title(recipe["title"])
    col1, col2 = st.columns([2,1])

    with col1:
        if recipe.get("image_url"):
            st.image(recipe["image_url"], use_container_width=True)

    with col2:
        if recipe.get("categories"):
            cats_html = " ".join([f'<span class="category-badge">{c}</span>' for c in recipe["categories"]])
            st.markdown(cats_html, unsafe_allow_html=True)
            st.markdown("")
        if recipe.get("tags"):
            tags_html = " ".join([f'<span class="tag">{t.strip()}</span>' for t in recipe["tags"].split(",") if t.strip()])
            st.markdown(tags_html, unsafe_allow_html=True)
            st.markdown("")
        if recipe.get("rating"):
            stars = "★" * int(recipe["rating"]) + "☆" * (5 - int(recipe["rating"]))
            st.markdown(f'<span class="rating">{stars}</span>', unsafe_allow_html=True)
        if recipe.get("servings"):
            st.markdown(f"**Servings:** {recipe['servings']}")
        if recipe.get("prep_time"):
            st.markdown(f"**Prep time:** {recipe['prep_time']}")
        if recipe.get("cook_time"):
            st.markdown(f"**Cook time:** {recipe['cook_time']}")
        if recipe.get("source_url"):
            st.markdown(f"[🔗 Original recipe]({recipe['source_url']})")

    if recipe.get("description"):
        st.markdown(f"_{recipe['description']}_")
    st.divider()
    if recipe.get("ingredients"):
        st.subheader("Ingredients")
        st.markdown(recipe["ingredients"])
    if recipe.get("instructions"):
        st.subheader("Instructions")
        st.markdown(recipe["instructions"])
    if recipe.get("notes"):
        st.subheader("Notes")
        st.info(recipe["notes"])

# ── EDIT PAGE ─────────────────────────────────────────────────
elif st.session_state.page == "edit":
    recipe = st.session_state.selected_recipe
    idx = st.session_state.selected_index

    if st.button("← Cancel"):
        st.session_state.page = "detail"
        st.rerun()

    st.title(f"Edit: {recipe['title']}")

    with st.form("edit_recipe_form"):
        data = recipe_form(existing=recipe)
        submitted = st.form_submit_button("Save changes", type="primary", use_container_width=True)
        if submitted:
            if not data["title"]:
                st.error("Please enter a recipe title.")
            else:
                with st.spinner("Saving..."):
                    update_recipe(idx, data)
                st.session_state.selected_recipe = data
                st.success(f"✅ '{data['title']}' updated!")
                st.session_state.page = "detail"
                st.rerun()

# ── HOME PAGE ─────────────────────────────────────────────────
elif st.session_state.page == "home":
    st.title("🍽️ Our Recipe Book")
    st.caption("A collection of our favourite dishes")

    with st.spinner("Loading recipes..."):
        recipes = load_recipes()

    col_search, col_add = st.columns([4,1])
    with col_search:
        search = st.text_input("", placeholder="🔍 Search recipes...", label_visibility="collapsed")
    with col_add:
        if st.button("+ Add recipe", use_container_width=True, type="primary"):
            st.session_state.page = "add"
            st.rerun()

    col_cat, col_tag, col_sort = st.columns(3)
    with col_cat:
        cat_filter = st.multiselect("Filter by category", CATEGORIES)
    with col_tag:
        all_tags = set()
        for r in recipes:
            if r.get("tags"):
                for t in r["tags"].split(","):
                    if t.strip(): all_tags.add(t.strip())
        tag_filter = st.multiselect("Filter by tag", sorted(all_tags))
    with col_sort:
        sort_by = st.selectbox("Sort by", ["Newest first","Oldest first","Rating (high to low)","A → Z"])

    filtered = list(recipes)
    if search:
        filtered = [r for r in filtered if search.lower() in r["title"].lower()
                    or search.lower() in r.get("description","").lower()]
    if cat_filter:
        filtered = [r for r in filtered if any(c in r.get("categories",[]) for c in cat_filter)]
    if tag_filter:
        filtered = [r for r in filtered if any(t in r.get("tags","") for t in tag_filter)]
    if sort_by == "Newest first":
        filtered = list(reversed(filtered))
    elif sort_by == "Rating (high to low)":
        filtered = sorted(filtered, key=lambda r: int(r.get("rating",0)), reverse=True)
    elif sort_by == "A → Z":
        filtered = sorted(filtered, key=lambda r: r["title"].lower())

    st.divider()

    if not recipes:
        st.markdown("### No recipes yet!")
        st.markdown("Click **+ Add recipe** to save your first dish. 🍳")
    elif not filtered:
        st.info("No recipes match your search.")
    else:
        st.caption(f"{len(filtered)} recipe{'s' if len(filtered) != 1 else ''}")
        cols = st.columns(3)
        for i, recipe in enumerate(filtered):
            original_index = recipes.index(recipe)
            with cols[i % 3]:
                with st.container(border=True):
                    if recipe.get("image_url"):
                        st.image(recipe["image_url"], use_container_width=True)
                    else:
                        st.markdown("🍽️")
                    st.markdown(f"**{recipe['title']}**")
                    if recipe.get("rating"):
                        stars = "★" * int(recipe["rating"]) + "☆" * (5 - int(recipe["rating"]))
                        st.markdown(f'<span class="rating" style="font-size:0.9rem">{stars}</span>', unsafe_allow_html=True)
                    if recipe.get("description"):
                        st.caption(recipe["description"][:80] + ("..." if len(recipe.get("description","")) > 80 else ""))
                    if recipe.get("categories"):
                        cats_html = " ".join([f'<span class="category-badge">{c}</span>' for c in recipe["categories"]])
                        st.markdown(cats_html, unsafe_allow_html=True)
                    if recipe.get("tags"):
                        tags_html = " ".join([f'<span class="tag">{t.strip()}</span>' for t in recipe["tags"].split(",") if t.strip()])
                        st.markdown(tags_html, unsafe_allow_html=True)
                    st.markdown("")
                    btn_col, del_col = st.columns([3,1])
                    with btn_col:
                        if st.button("View recipe", key=f"view_{original_index}", use_container_width=True):
                            st.session_state.selected_recipe = recipe
                            st.session_state.selected_index = original_index
                            st.session_state.page = "detail"
                            st.rerun()
                    with del_col:
                        if st.button("🗑️", key=f"del_{original_index}", help="Delete recipe"):
                            delete_recipe(original_index)

# ── ADD RECIPE PAGE ───────────────────────────────────────────
elif st.session_state.page == "add":
    if st.button("← Cancel"):
        st.session_state.page = "home"
        st.rerun()

    st.title("Add a new recipe")

    with st.form("add_recipe_form"):
        data = recipe_form()
        submitted = st.form_submit_button("Save recipe", type="primary", use_container_width=True)
        if submitted:
            if not data["title"]:
                st.error("Please enter a recipe title.")
            else:
                with st.spinner("Saving..."):
                    save_new_recipe(data)
                st.success(f"✅ '{data['title']}' saved!")
                st.cache_resource.clear()
                st.session_state.page = "home"
                st.rerun()
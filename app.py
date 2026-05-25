import streamlit as st
import json
import os
from pathlib import Path

RECIPES_FILE = "recipes.json"

def load_recipes():
    if not Path(RECIPES_FILE).exists():
        return []
    with open(RECIPES_FILE, "r") as f:
        return json.load(f)

def save_recipes(recipes):
    with open(RECIPES_FILE, "w") as f:
        json.dump(recipes, f, indent=2)

def delete_recipe(index):
    recipes = load_recipes()
    recipes.pop(index)
    save_recipes(recipes)
    st.rerun()

# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="Our Recipe Book", page_icon="🍽️", layout="wide")

st.markdown("""
<style>
    .recipe-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
        transition: box-shadow 0.2s;
    }
    .recipe-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .tag {
        display: inline-block;
        background: #fff3e0;
        color: #e65100;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        margin-right: 4px;
    }
    .rating { color: #f5a623; font-size: 1.1rem; }
    h1 { font-size: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Routing via session state ─────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_recipe" not in st.session_state:
    st.session_state.selected_recipe = None

# ── DETAIL PAGE ───────────────────────────────────────────────
if st.session_state.page == "detail":
    recipe = st.session_state.selected_recipe

    if st.button("← Back to all recipes"):
        st.session_state.page = "home"
        st.rerun()

    st.title(recipe["title"])

    col1, col2 = st.columns([2, 1])

    with col1:
        if recipe.get("image_url"):
            st.image(recipe["image_url"], use_container_width=True)

    with col2:
        if recipe.get("tags"):
            tags_html = " ".join([f'<span class="tag">{t.strip()}</span>' for t in recipe["tags"].split(",")])
            st.markdown(tags_html, unsafe_allow_html=True)

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

# ── HOME PAGE ─────────────────────────────────────────────────
elif st.session_state.page == "home":
    st.title("🍽️ Our Recipe Book")
    st.caption("A collection of our favourite dishes")

    recipes = load_recipes()

    # Top bar: search + add button
    col_search, col_add = st.columns([4, 1])
    with col_search:
        search = st.text_input("", placeholder="🔍 Search recipes...", label_visibility="collapsed")
    with col_add:
        if st.button("+ Add recipe", use_container_width=True, type="primary"):
            st.session_state.page = "add"
            st.rerun()

    # Filter + sort
    col_filter, col_sort = st.columns(2)
    with col_filter:
        all_tags = set()
        for r in recipes:
            if r.get("tags"):
                for t in r["tags"].split(","):
                    all_tags.add(t.strip())
        tag_filter = st.multiselect("Filter by tag", sorted(all_tags))
    with col_sort:
        sort_by = st.selectbox("Sort by", ["Newest first", "Oldest first", "Rating (high to low)", "A → Z"])

    # Apply search + filter
    filtered = recipes
    if search:
        filtered = [r for r in filtered if search.lower() in r["title"].lower() or search.lower() in r.get("description", "").lower()]
    if tag_filter:
        filtered = [r for r in filtered if any(t in r.get("tags", "") for t in tag_filter)]

    # Apply sort
    if sort_by == "Oldest first":
        filtered = list(filtered)
    elif sort_by == "Newest first":
        filtered = list(reversed(filtered))
    elif sort_by == "Rating (high to low)":
        filtered = sorted(filtered, key=lambda r: int(r.get("rating", 0)), reverse=True)
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

                    if recipe.get("tags"):
                        tags_html = " ".join([f'<span class="tag">{t.strip()}</span>' for t in recipe["tags"].split(",")])
                        st.markdown(tags_html, unsafe_allow_html=True)
                        st.markdown("")

                    btn_col, del_col = st.columns([3, 1])
                    with btn_col:
                        if st.button("View recipe", key=f"view_{original_index}", use_container_width=True):
                            st.session_state.selected_recipe = recipe
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
        st.subheader("Basic info")
        title = st.text_input("Recipe title *", placeholder="e.g. Pasta Carbonara")
        description = st.text_area("Short description", placeholder="A quick one-liner about the dish", height=70)
        image_url = st.text_input("Image URL", placeholder="Paste an image link from Google Photos, Imgur, etc.")
        source_url = st.text_input("Source / recipe link", placeholder="Link to the original recipe (optional)")

        col1, col2, col3 = st.columns(3)
        with col1:
            servings = st.text_input("Servings", placeholder="e.g. 4")
        with col2:
            prep_time = st.text_input("Prep time", placeholder="e.g. 15 min")
        with col3:
            cook_time = st.text_input("Cook time", placeholder="e.g. 30 min")

        rating = st.select_slider("Rating", options=[1, 2, 3, 4, 5], value=5)
        tags = st.text_input("Tags (comma separated)", placeholder="e.g. Italian, pasta, quick")

        st.subheader("Recipe details")
        st.caption("You can use markdown: **bold**, _italic_, - bullet lists, 1. numbered lists")
        ingredients = st.text_area("Ingredients", placeholder="- 200g spaghetti\n- 2 eggs\n- 100g pancetta", height=150)
        instructions = st.text_area("Instructions", placeholder="1. Boil pasta...\n2. Fry pancetta...", height=200)
        notes = st.text_area("Notes / tips", placeholder="Any extra tips, substitutions, or variations", height=80)

        submitted = st.form_submit_button("Save recipe", type="primary", use_container_width=True)

        if submitted:
            if not title:
                st.error("Please enter a recipe title.")
            else:
                new_recipe = {
                    "title": title,
                    "description": description,
                    "image_url": image_url,
                    "source_url": source_url,
                    "servings": servings,
                    "prep_time": prep_time,
                    "cook_time": cook_time,
                    "rating": rating,
                    "tags": tags,
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "notes": notes,
                }
                recipes = load_recipes()
                recipes.append(new_recipe)
                save_recipes(recipes)
                st.success(f"✅ '{title}' saved!")
                st.session_state.page = "home"
                st.rerun()
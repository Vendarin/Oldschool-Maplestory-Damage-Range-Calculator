from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Weapon multipliers and classifications.
# IMPORTANT: ensure your frontend sends one of these exact keys for "weapon".
weapon_data = {
    "One Handed Sword":        {"primary": ("STR", 4.0), "secondary": "DEX", "type": "physical"},
    "One Handed Axe/BW/Wand/Staff (Swinging)": {"primary": ("STR", 4.4), "secondary": "DEX", "type": "physical"},
    "Two Handed Sword":        {"primary": ("STR", 4.6), "secondary": "DEX", "type": "physical"},
    "Two Handed Axe/BW (Swinging)": {"primary": ("STR", 4.8), "secondary": "DEX", "type": "physical"},
    "Spear (Stabbing)":        {"primary": ("STR", 5.0), "secondary": "DEX", "type": "physical"},
    "Polearm (Swinging)":      {"primary": ("STR", 5.0), "secondary": "DEX", "type": "physical"},
    "Dagger (Non-Thieves)":    {"primary": ("STR", 4.0), "secondary": "DEX", "type": "physical"},
    "Dagger/Throwing Stars (Thieves)": {"primary": ("LUK", 3.6), "secondary": "STR+DEX", "type": "physical"},
    "Bow":                     {"primary": ("DEX", 3.4), "secondary": "STR", "type": "physical"},
    "Crossbow":                {"primary": ("DEX", 3.6), "secondary": "STR", "type": "physical"},
    "Knuckle":                 {"primary": ("STR", 4.8), "secondary": "DEX", "type": "physical"},
    "Gun":                     {"primary": ("DEX", 3.6), "secondary": "STR", "type": "physical"},
    # Explicit magic entries (frontend should send "Wand" or "Staff" for magic formula)
    "Wand":                    {"primary": ("INT", 1.0), "secondary": "LUK", "type": "magic"},
    "Staff":                   {"primary": ("INT", 1.0), "secondary": "LUK", "type": "magic"},
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()

    weapon_key = data.get("weapon")
    weapon = weapon_data.get(weapon_key)
    if not weapon:
        return jsonify({"error": f"Invalid weapon type: {weapon_key}"}), 400

    # base stats from front-end
    STR  = float(data.get("STR", 0) or 0)
    DEX  = float(data.get("DEX", 0) or 0)
    INT  = float(data.get("INT", 0) or 0)
    LUK  = float(data.get("LUK", 0) or 0)
    ATT  = float(data.get("ATT", 0) or 0)   
    MATT = float(data.get("MATT", 0) or 0)  

    mastery = float(data.get("mastery", 0.6))

    if weapon["type"] == "magic":
        magic = MATT  
        spell_attack = 290

        max_dmg = ((magic ** 2 / 1000.0 + magic) / 30.0 + INT / 200.0) * spell_attack
        min_dmg = ((magic ** 2 / 1000.0 + magic * mastery * 0.9) / 30.0 + INT / 200.0) * spell_attack

    else:
        primary_stat_name, multiplier = weapon["primary"]
        prim_raw = {"STR": STR, "DEX": DEX, "INT": INT, "LUK": LUK}.get(primary_stat_name, 0.0)
        
        if weapon_data["Spear (Stabbing)"]:
            primary = prim_raw * 3
        primary = prim_raw * float(multiplier)

        sec = weapon["secondary"]
        if sec == "STR+DEX":
            secondary = STR + DEX
        elif sec == "STR":
            secondary = STR
        elif sec == "DEX":
            secondary = DEX
        elif sec == "LUK":
            secondary = LUK
        else:
            secondary = 0.0

        if "Spear" in weapon_key:
            spear_primary = prim_raw * 3.0
            min_dmg = (spear_primary * 0.9 * mastery + secondary) * ATT / 100.0
        elif "Polearm" in weapon_key:
            spear_primary = prim_raw * 3.0
            min_dmg = (spear_primary * 0.9 * mastery + secondary) * ATT / 100.0
        else:
            min_dmg = (primary * 0.9 * mastery + secondary) * ATT / 100.0

        max_dmg = (primary + secondary) * ATT / 100.0


    max_dmg = max(0.0, max_dmg)
    min_dmg = max(0.0, min_dmg)

    max_dmg = int(max_dmg)
    min_dmg = int(min_dmg)

    return jsonify({
        "min": round(min_dmg, 0),
        "max": round(max_dmg, 0)
    })

#if __name__ == "__main__":
#    app.run(debug=True)





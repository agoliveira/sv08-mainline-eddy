#!/usr/bin/env python3
# Adds beeper signals to the SV08 mainline configuration.
# Edits macros.cfg and printer.cfg in place, after saving a copy of each.
# If any expected text is not found, nothing is written.
import os, shutil, sys, time

CONFIG_DIR = os.path.expanduser("~/printer_data/config")
if len(sys.argv) > 1:
    CONFIG_DIR = sys.argv[1]
MACROS = os.path.join(CONFIG_DIR, "macros.cfg")
PRINTER = os.path.join(CONFIG_DIR, "printer.cfg")

EDITS_MACROS = [
    # (description, old text, new text)
    ("BEEP macro",
     "[gcode_macro BEEP]\ngcode:\n    SET_PIN PIN=beeper VALUE=1\n    G4 P10\n    SET_PIN PIN=beeper VALUE=0\n",
     "# BEEP COUNT=<n> MS=<on time> PAUSE=<off time>\n"
     "# Times are in milliseconds, with a minimum of 100 each.\n"
     "# Set variable_beeper_enabled to False in _global_var to silence it.\n"
     "[gcode_macro BEEP]\n"
     "gcode:\n"
     "    {% set count = params.COUNT|default(1)|int %}\n"
     "    {% set ms = [params.MS|default(100)|int, 100]|max %}\n"
     "    {% set pause = [params.PAUSE|default(100)|int, 100]|max %}\n"
     "    {% if printer['gcode_macro _global_var'].beeper_enabled %}\n"
     "        {% for i in range(count) %}\n"
     "            SET_PIN PIN=beeper VALUE=1\n"
     "            G4 P{ms}\n"
     "            SET_PIN PIN=beeper VALUE=0\n"
     "            G4 P{pause}\n"
     "        {% endfor %}\n"
     "    {% endif %}\n"),
    ("beeper switch in _global_var",
     "variable_z_maximum_lifting_distance: 345\n",
     "variable_z_maximum_lifting_distance: 345\n"
     "# Master switch for all beeper signals.\n"
     "variable_beeper_enabled: True\n"),
    ("signal at the end of START_PRINT",
     "    _PURGE_LINE EXTRUDER_TEMP={extruder_temp}\n    M117 Printing\n",
     "    _PURGE_LINE EXTRUDER_TEMP={extruder_temp}\n    M117 Printing\n"
     "    # One beep: the first layer is about to start.\n"
     "    BEEP MS=200\n"),
    ("signal at the end of END_PRINT",
     "    {action_respond_info(\"Finish Print!\")}\n",
     "    {action_respond_info(\"Finish Print!\")}\n"
     "    # Three beeps: print finished.\n"
     "    BEEP COUNT=3 MS=150 PAUSE=150\n"),
    ("alarm on M600",
     "[gcode_macro M600]\ngcode:\n    PAUSE\n",
     "[gcode_macro M600]\ngcode:\n    PAUSE\n"
     "    UPDATE_DELAYED_GCODE ID=attention_alarm DURATION=1\n"),
]

APPEND_MACROS = (
    "\n"
    "# Repeating alarm for a print that is paused and waiting for someone:\n"
    "# filament runout or a filament change (M600). Five long beeps, again\n"
    "# every 30 seconds, until the print is resumed or cancelled.\n"
    "# Started with: UPDATE_DELAYED_GCODE ID=attention_alarm DURATION=1\n"
    "[delayed_gcode attention_alarm]\n"
    "gcode:\n"
    "    {% if printer.pause_resume.is_paused %}\n"
    "        BEEP COUNT=5 MS=300 PAUSE=150\n"
    "        UPDATE_DELAYED_GCODE ID=attention_alarm DURATION=30\n"
    "    {% endif %}\n"
)

EDITS_PRINTER = [
    ("alarm on filament runout",
     "pause_delay: 0.5\nswitch_pin: PE9\n",
     "pause_delay: 0.5\nswitch_pin: PE9\n"
     "runout_gcode:\n"
     "    M117 Filament runout\n"
     "    UPDATE_DELAYED_GCODE ID=attention_alarm DURATION=1\n"),
]

def apply(path, edits, append=""):
    with open(path) as f:
        text = f.read()
    if "attention_alarm" in text:
        sys.exit("%s already contains the beeper changes. Nothing done." % path)
    for desc, old, new in edits:
        if text.count(old) != 1:
            sys.exit("Could not find the place for: %s (in %s). Nothing was changed."
                     % (desc, path))
        text = text.replace(old, new)
    return text + append

new_macros = apply(MACROS, EDITS_MACROS, APPEND_MACROS)
new_printer = apply(PRINTER, EDITS_PRINTER)
stamp = time.strftime("%Y%m%d_%H%M%S")
for path, text in ((MACROS, new_macros), (PRINTER, new_printer)):
    shutil.copy2(path, "%s.before-beeper-%s" % (path, stamp))
    with open(path, "w") as f:
        f.write(text)
    print("Updated %s" % path)
print("Done. Copies of the previous files end in .before-beeper-%s" % stamp)

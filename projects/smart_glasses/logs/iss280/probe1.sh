set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "=== md5 protected 5 ==="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "=== mtime board ==="
stat -c '%y %n' HW/PCB/demo_mainboard.kicad_pcb
echo "=== production pack ==="
find HW/PCB/production -type f | wc -l
find HW/PCB/gerbers -type f | wc -l
echo "=== fragments ==="
ls -la state/fragments/ | head -20
echo "=== existing HW checks ==="
ls -la HW/*.py
echo "=== state scripts ==="
ls state/*.py | head -40

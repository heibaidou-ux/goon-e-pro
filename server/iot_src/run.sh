#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
case "$1" in
  list)     python scripts/query_states.py ;;
  on)       python scripts/control_light.py on "$2" ;;
  off)      python scripts/control_light.py off "$2" ;;
  toggle)   python scripts/control_light.py toggle "$2" ;;
  scene)    python scripts/control_light.py scene "$2" ;;
  panel)    python scripts/simulate_panel.py list ;;
  press)    python scripts/simulate_panel.py press "$2" ;;
  mock)     python mock_ha.py ;;
  bridge)   python mqtt_bridge/bridge.py ;;
  *)        echo "Usage: ./run.sh {list|on|off|toggle|scene|panel|press|mock|bridge}" ;;
esac

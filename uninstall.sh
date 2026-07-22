#!/bin/sh
set -eu

DATA_HOME=${XDG_DATA_HOME:-"$HOME/.local/share"}
APP_DIR="$DATA_HOME/checklist-app"
BIN_PATH="$HOME/.local/bin/checklist"
DESKTOP_DIR="$DATA_HOME/applications"
DESKTOP_PATH="$DESKTOP_DIR/checklist.desktop"
ICON_PATH="$DATA_HOME/icons/hicolor/256x256/apps/checklist.png"

rm -f -- "$BIN_PATH" "$DESKTOP_PATH" "$ICON_PATH"
rm -rf -- "$APP_DIR"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$DESKTOP_DIR"
fi

printf '%s
' "checklist uninstalled. Your saved checklist data was kept."

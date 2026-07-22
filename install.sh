#!/bin/sh
set -eu

SOURCE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DATA_HOME=${XDG_DATA_HOME:-"$HOME/.local/share"}
APP_DIR="$DATA_HOME/checklist-app"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$DATA_HOME/applications"
ICON_DIR="$DATA_HOME/icons/hicolor/256x256/apps"

mkdir -p "$APP_DIR/assets/fonts" "$BIN_DIR" "$DESKTOP_DIR" "$ICON_DIR"
cp "$SOURCE_DIR/main.py" "$SOURCE_DIR/run.sh" "$SOURCE_DIR/icon.png" "$APP_DIR/"
cp "$SOURCE_DIR/assets/fonts/Pretendard-Regular.otf" \
  "$SOURCE_DIR/assets/fonts/LICENSE.txt" "$APP_DIR/assets/fonts/"
chmod +x "$APP_DIR/run.sh"
ln -sfn "$APP_DIR/run.sh" "$BIN_DIR/checklist"
cp "$SOURCE_DIR/icon.png" "$ICON_DIR/checklist.png"
sed "s|@APP_DIR@|$APP_DIR|g" "$SOURCE_DIR/checklist.desktop.in"   > "$DESKTOP_DIR/checklist.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$DESKTOP_DIR"
fi

printf '%s
' "checklist installed. Run it from the app menu or with: checklist"

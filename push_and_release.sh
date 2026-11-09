#!/usr/bin/env bash
# push_and_release.sh — create the GitHub repo, push the show, ship the release.
#
# Usage:
#   export GITHUB_TOKEN=github_pat_xxxxx      # fine-grained PAT (see README)
#   export REPO=shinyobjectz/demon-lord-pay-rent   # optional, this is the default
#   export ASSET_DIR=.                        # dir containing release assets (optional)
#   ./push_and_release.sh
#
# Assets expected in ASSET_DIR (any that exist will be uploaded):
#   dlpr_animatic_preview.mp4  demon-lord-pay-rent.zip  theme.mp3
set -euo pipefail

: "${GITHUB_TOKEN:?Set GITHUB_TOKEN (a fine-grained PAT with Administration: RW + Contents: RW)}"
REPO="${REPO:-shinyobjectz/demon-lord-pay-rent}"
NAME="${REPO#*/}"
TAG="v0.1.0"
API="https://api.github.com"
ASSET_DIR="${ASSET_DIR:-.}"

echo "==> Creating repo $REPO (ok if it already exists)"
curl -s -o create.json -w "%{http_code}\n" -X POST "$API/user/repos" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -d "{\"name\":\"$NAME\",\"description\":\"DEMON LORD, PAY RENT! — anime sitcom rendered by raea. No video models, just your GPU.\",\"private\":false,\"has_wiki\":false}" \
  | grep -qE "20[0-9]" && echo "    created" || { echo "    create skipped/failed:"; head -c 400 create.json; echo; }
rm -f create.json

echo "==> Pushing main + tag $TAG"
git remote remove origin 2>/dev/null || true
git remote add origin "https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO}.git"
git push -u origin HEAD:main
git push origin "$TAG" 2>/dev/null || git tag -a "$TAG" -m "Episode 1 — The Rent Must Flow" && git push origin "$TAG"
git remote set-url origin "https://github.com/${REPO}.git"   # scrub token from .git/config

echo "==> Creating release $TAG"
BODY_FILE="$(mktemp)"
python3 - "$BODY_FILE" <<'PY'
import json,sys
body=open("RELEASE_NOTES.md",encoding="utf-8").read()
json.dump({"tag_name":"v0.1.0","name":"Episode 1 — The Rent Must Flow",
           "body":body,"draft":False,"prerelease":False},open(sys.argv[1],"w"))
PY
HTTP=$(curl -s -o release.json -w "%{http_code}" -X POST "$API/repos/$REPO/releases" \
  -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" \
  --data-binary @"$BODY_FILE")
if [ "$HTTP" != "201" ]; then echo "    release create failed ($HTTP):"; head -c 500 release.json; echo
  echo "    (if release already exists, fetching its id)"
  curl -s "$API/repos/$REPO/releases/tags/$TAG" -H "Authorization: Bearer $GITHUB_TOKEN" -o release.json
fi
RELEASE_ID=$(python3 -c "import json;print(json.load(open('release.json'))['id'])")
echo "    release id $RELEASE_ID"
rm -f "$BODY_FILE"

upload () {  # upload <file> <content-type>
  F="$1"; CT="$2"
  [ -f "$ASSET_DIR/$F" ] || { echo "    skip $F (not found in $ASSET_DIR)"; return 0; }
  echo "    uploading $F"
  curl -s -o /dev/null -X POST \
    "https://uploads.github.com/repos/$REPO/releases/$RELEASE_ID/assets?name=$F" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -H "Content-Type: $CT" \
    --data-binary @"$ASSET_DIR/$F"
}
upload dlpr_animatic_preview.mp4 video/mp4
upload demon-lord-pay-rent.zip   application/zip
upload theme.mp3                 audio/mpeg

echo "==> Done: https://github.com/$REPO/releases/tag/$TAG"

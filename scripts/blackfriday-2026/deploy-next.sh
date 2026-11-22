#!/bin/zsh
# 요금제 링크를 넣은 앱을 하나씩 DeployBar 로 배포한다. launchd 가 15분마다 부른다(한 번에 하나만 돈다).
#   deploy-queue.txt 의 줄("앱이름|추가 인자") 중 아직 안 끝난 것 하나를 고른다.
#   다른 배포가 돌고 있으면 그냥 끝낸다. 앱이 심사 중이라 거절되면(코드 3) 30분 뒤 다시 본다.
#   모두 끝나면 예약을 스스로 지운다.
D=/Applications/DeployBar.app/Contents/MacOS/DeployBar
cd "$(dirname $0)"; touch deploy-queue.txt deploy-done.txt deploy-wait.txt
now=$(date +%s); next=""
for l in "${(@f)$(grep -vxFf deploy-done.txt deploy-queue.txt)}"; do
  [ -z "$l" ] && continue
  t=$(grep -F "$l|@" deploy-wait.txt | tail -1 | awk -F'|@' '{print $2}')
  if [ -z "$t" ] || [ $((now - t)) -gt 1800 ]; then next=$l; break; fi
done
if [ -z "$(grep -vxFf deploy-done.txt deploy-queue.txt)" ]; then
  echo "── $(date '+%m/%d %H:%M') 큐 끝"; p=~/Library/LaunchAgents/com.leeo.blackfriday-deploy.plist
  launchctl unload "$p"; rm -f "$p"; exit 0
fi
[ -z "$next" ] && exit 0
$D --ready 2>/dev/null | grep -q "지금 배포 중" && exit 0
app=${next%%|*}; args=${next#*|}; [ "$args" = "$next" ] && args=""
echo "── $(date '+%m/%d %H:%M') 배포 시작 $app $args"
$D --deploy "$app" ${=args} --quiet > "deploy-logs/$app.log" 2>&1; code=$?
echo "── $(date '+%m/%d %H:%M') $app 끝 코드 $code · $(tail -1 "deploy-logs/$app.log")"
if [ $code = 3 ]; then echo "$next|@$(date +%s)" >> deploy-wait.txt; else echo "$next" >> deploy-done.txt; fi

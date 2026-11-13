"""Chơi thử tự động FIRELINE '68 (dành cho bot QA).
Chạy: python3 tools/playtest.py
Kịch bản: (1) chiến dịch 40s, người chơi tự ngắm bắn, địch bắn trả, chụp ảnh liên tục;
(2) điện thoại xoay ngang 844x390, cảm ứng; (3) 2 người chơi online qua máy chủ WebSocket cục bộ.
Ghi lỗi JS + ảnh vào tools/shots/playtest_*.png. Thoát mã 1 nếu có lỗi."""
import asyncio, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check
from check import ROOT
URL='http://127.0.0.1:8799/'
ARGS=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']
AIMBOT="""(()=>{const g=window.__game,p=g.player; if(!p.alive) return 'dead'; const e=g.enemies.filter(e=>e.alive&&e.los)[0];
 if(e){ const dx=e.pos.x-p.pos.x, dz=e.pos.z-p.pos.z, dy=(e.pos.y+1.2)-(p.pos.y+p.eye); p.yaw=Math.atan2(-dx,-dz); p.pitch=Math.atan2(dy,Math.hypot(dx,dz)); p.fireHeld=true; } else p.fireHeld=false;
 return JSON.stringify({hp:Math.round(p.hp),wave:g.state.wave,kills:g.state.kills,alive:g.enemies.filter(e=>e.alive).length}); })()"""
async def new_page(b, errs, tag, **kw):
    q=kw.pop('q','med'); ctx=await b.new_context(**kw); await ctx.add_init_script("try{localStorage.setItem('tl_quality4', JSON.stringify('%s'))}catch(e){}" % q)
    pg=await ctx.new_page(); pg.set_default_timeout(300000)
    pg.on('pageerror', lambda e: errs.append(f'[{tag}] pageerror: {e}'))
    pg.on('console', lambda m: errs.append(f'[{tag}] console: {m.text}') if m.type=='error' and '404' not in m.text else None)
    await pg.goto(URL); await pg.wait_for_function('window.__gameReady===true', timeout=300000); return pg
async def run():
    from playwright.async_api import async_playwright
    shots=f'{ROOT}/tools/shots'; os.makedirs(shots, exist_ok=True); errs=[]; report={}
    async with async_playwright() as p:
        exe='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None
        b=await p.chromium.launch(executable_path=exe, args=ARGS)
        # 1) campaign combat
        pg=await new_page(b, errs, 'campaign', viewport={'width':960,'height':540})
        await pg.evaluate("window.__game.state.diff=1; window.__game.startCampaign(); window.__game.state.waveT=0.5")
        log=[]
        for i in range(20):
            await pg.wait_for_timeout(2000); log.append(await pg.evaluate(AIMBOT))
            if i%5==4: await pg.screenshot(path=f'{shots}/playtest_combat_{i//5}.png')
        report['campaign']=log[-5:]
        for w in range(4):
            await pg.evaluate(f"window.__game.switchWeapon({w})"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'{shots}/playtest_weapons.png')
        await pg.context.close()
        # 2) mobile landscape
        pg=await new_page(b, errs, 'mobile', viewport={'width':844,'height':390}, is_mobile=True, has_touch=True)
        await pg.screenshot(path=f'{shots}/playtest_mobile_menu.png')
        await pg.tap('#mCampaign'); await pg.wait_for_timeout(800); await pg.tap('#mStart'); await pg.wait_for_timeout(5000)
        await pg.tap('#bFire'); await pg.tap('#bSwap'); await pg.tap('#bAim'); await pg.wait_for_timeout(2000)
        await pg.screenshot(path=f'{shots}/playtest_mobile_play.png')
        report['mobile_touch_ui']=await pg.evaluate("!document.getElementById('touch').classList.contains('hidden')")
        await pg.context.close()
        # 3) online 2 players
        a=await new_page(b, errs, 'online-A', viewport={'width':480,'height':270}, q='low'); c=await new_page(b, errs, 'online-B', viewport={'width':480,'height':270}, q='low')
        for pg in (a,c):
            await pg.evaluate("document.getElementById('mOnline').click()"); await pg.wait_for_timeout(3000)
            await pg.wait_for_function("!document.getElementById('mJoin').disabled && document.getElementById('netStatus').textContent.includes('Sẵn sàng')", timeout=60000)
        # A tạo phòng, B thấy phòng trong danh sách và bấm vào (không nhập mã)
        await a.evaluate("document.getElementById('mCreate').click()"); await a.wait_for_timeout(500); await a.screenshot(path=f'{shots}/playtest_create.png')
        await a.fill('#roomCode','QA Kiểm thử'); await a.evaluate("document.getElementById('mJoin').click()")
        await a.wait_for_function("window.__game.state.mode==='online'", timeout=60000)
        await c.wait_for_function("[...document.querySelectorAll('#roomList .roomc')].some(b=>b.textContent.includes('QA Kiểm thử'))", timeout=60000)
        report['room_list']=await c.evaluate("[...document.querySelectorAll('#roomList .roomc b')].map(b=>b.textContent)")
        await c.screenshot(path=f'{shots}/playtest_roomlist.png')
        await c.evaluate("window.__autoSide='us'; [...document.querySelectorAll('#roomList .roomc')].find(b=>b.textContent.includes('QA Kiểm thử')).click()")
        await c.wait_for_function("window.__game.state.mode==='online'", timeout=60000)
        for _ in range(30):  # SwiftShader rất chậm: chờ tối đa ~60s
            await a.wait_for_timeout(2000)
            report['online_peers_A']=await a.evaluate("window.__game.net.remotes.size")
            report['online_peers_B']=await c.evaluate("window.__game.net.remotes.size")
            if report['online_peers_A']>=1 and report['online_peers_B']>=1: break
        # đấu đội: A là host điều khiển bot, B (phe Mỹ) thấy bot qua mạng
        for _ in range(30):
            await a.wait_for_timeout(2000)
            report['tdm_A']=await a.evaluate("(()=>{const g=window.__game,n=g.net; return {tdm:n.tdm, host:n.isHost(), side:g.player.side, allies:g.allies.length, enemies:g.enemies.filter(e=>e.alive).length, ts:n.ts}})()")
            report['tdm_B']=await c.evaluate("(()=>{const g=window.__game,n=g.net; return {tdm:n.tdm, host:n.isHost(), side:g.player.side, puppets:n.puppets.size, ts:n.ts}})()")
            if report['tdm_B']['puppets']>=6: break
        await a.screenshot(path=f'{shots}/playtest_online.png'); await c.screenshot(path=f'{shots}/playtest_online_B.png')
        if report['online_peers_A']<1 or report['online_peers_B']<1: errs.append('online: 2 người chơi không thấy nhau')
        if not report['tdm_A']['host'] or report['tdm_B']['host']: errs.append('đấu đội: chọn host sai')
        if report['tdm_B']['puppets']<6: errs.append('đấu đội: máy B không thấy bot')
        if report['tdm_B']['side']!='us': errs.append('đấu đội: B không vào được phe Mỹ')
        await b.close()
    return errs, report
if __name__=='__main__':
    check.prep(); pr=check.server()
    try: errs,report=asyncio.run(run())
    finally: pr.terminate()
    print(json.dumps({'errors':errs[:30],'report':report}, ensure_ascii=False, indent=1))
    print('KẾT QUẢ:', 'ĐẠT' if not errs else 'CÓ LỖI'); sys.exit(0 if not errs else 1)

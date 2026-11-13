"""Kiểm tra XUNG PHONG: quét sạch địch -> toàn đội +30% máu: python3 tools/rushtest.py"""
import asyncio, os, sys, json
sys.argv=[sys.argv[0]]+(sys.argv[1:] or ['high'])
import check
async def run():
    from playwright.async_api import async_playwright
    errs=[]; rep={}
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None, args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':844,'height':390}, is_mobile=True, has_touch=True); await ctx.add_init_script(f"try{{localStorage.setItem('tl_quality4', JSON.stringify('{check.Q}'))}}catch(e){{}}")
        pg=await ctx.new_page(); pg.set_default_timeout(300000); pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true', timeout=300000)
        await pg.evaluate("(async()=>{ const g=window.__game; g.settings.map='khesanh'; g.settings.mode='base'; await g.startCampaign(); g.player.invuln=9999; g.state.matchT=20; g.state.timeScale=3; })()")
        await pg.wait_for_function("window.__game.state.phase==='playing'", timeout=200000)
        await pg.wait_for_function("window.__game.enemies.some(e=>e.alive)", timeout=200000)
        await pg.evaluate("(()=>{ const g=window.__game; g.state.hadFoes=true; for(const e of g.enemies) if(e.alive) g.damageEnemy(e, 9999, false, null, true); g.state.enQ.length=0; g.state.enMax=0; })()")
        await pg.wait_for_function("(window.__game.state.rushT||0)>0", timeout=300000)
        await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{check.ROOT}/tools/shots/rush.png')
        rep=await pg.evaluate("(()=>{ const g=window.__game; return {rushT:+g.state.rushT.toFixed(1), hp:Math.round(g.player.hp), allyHp:g.allies.filter(a=>a.alive).map(a=>Math.round(a.hp))}; })()")
        await b.close()
    return errs, rep
check.prep(); pr=check.server()
try: errs,rep=asyncio.run(run())
finally: pr.terminate()
ok=not errs and rep.get('hp',0)>=129 and all(h>=190 for h in rep.get('allyHp',[0]))
print(json.dumps({'errors':errs,'report':rep},ensure_ascii=False)); print('KẾT QUẢ:', 'ĐẠT' if ok else 'CÓ LỖI')

"""Kiểm tra các chế độ chơi mới: python3 tools/modetest.py [low|high]"""
import asyncio, os, sys, json
sys.argv=[sys.argv[0]]+(sys.argv[1:] or ['high'])
import check
async def run():
    from playwright.async_api import async_playwright
    shots=f'{check.ROOT}/tools/shots'; errs=[]; rep={}
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None, args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':960,'height':540}); await ctx.add_init_script(f"try{{localStorage.setItem('tl_quality3', JSON.stringify('{check.Q}'))}}catch(e){{}}")
        pg=await ctx.new_page(); pg.set_default_timeout(300000)
        pg.on('pageerror', lambda e: errs.append('pageerror: '+str(e)))
        pg.on('console', lambda m: errs.append('console: '+m.text) if m.type=='error' and '404' not in m.text else None)
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true', timeout=300000)
        for mp,mode in (('khesanh','base'),('himlam','bunker'),('cuchi','base')):
            await pg.evaluate(f"(async()=>{{ const g=window.__game; g.settings.map='{mp}'; g.settings.mode='{mode}'; await g.startCampaign(); }})()")
            await pg.wait_for_function("window.__game.state.phase==='playing'", timeout=300000)
            await pg.wait_for_timeout(3000)
            await pg.screenshot(path=f'{shots}/mode_{mp}_1.png')
            await pg.evaluate("""(()=>{ const g=window.__game; g.state.money=999999; g.shopBuy('rpd'); g.shopBuy('nade'); g.shopBuy('ally'); g.playerThrow(); g.toggleProne(); g.supplyDrop(); })()""")
            await pg.wait_for_timeout(3500)
            await pg.screenshot(path=f'{shots}/mode_{mp}_2.png')
            rep[mp]=await pg.evaluate("""(()=>{ const g=window.__game, s=g.state; return {mission:s.mission, phase:s.phase, money:s.money, enemies:g.enemies.filter(e=>e.alive).length, allies:g.allies.length, hqs:g.hqs.map(h=>h.side+':'+Math.round(h.hp)), arts:g.arts.length, crates:g.crates.length, caps:g.capCells.length, cur:g.player.cur, prone:g.player.prone, kVN:s.kVN, kEN:s.kEN, roles:[...new Set(g.allies.map(a=>a.role))].join(',')}; })()""")
            # bot vs bot: để mô phỏng chạy thêm
            await pg.evaluate("(()=>{ const g=window.__game; g.player.invuln=999; })()")
            await pg.wait_for_timeout(6000)
            await pg.screenshot(path=f'{shots}/mode_{mp}_3.png')
            rep[mp+'_later']=await pg.evaluate("(()=>{ const g=window.__game, s=g.state; return {phase:s.phase,kVN:s.kVN,kEN:s.kEN,enemies:g.enemies.filter(e=>e.alive).length, enQ:(s.enQ||[]).length, hqs:g.hqs.map(h=>h.side+':'+Math.round(h.hp)), cap:s.capIdx+'/'+s.capProg.toFixed(1)}; })()")
        await b.close()
    return errs, rep
check.prep(); pr=check.server()
try:
    errs,rep=asyncio.run(run()); print(json.dumps({'errors':errs[:20],'report':rep},ensure_ascii=False,indent=1)); print('KẾT QUẢ:', 'ĐẠT' if not errs else 'CÓ LỖI')
finally: pr.terminate()

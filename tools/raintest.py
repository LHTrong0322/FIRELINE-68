"""Chụp vũng nước gợn mưa ở Đồi A1 (đêm mưa): python3 tools/raintest.py [low|high]
So sánh có/không gợn (BAKE_U.rainU.x) cùng góc máy, cạnh đống lửa gần nhất."""
import asyncio, os, sys
sys.argv=[sys.argv[0]]+(sys.argv[1:] or ['high'])
import check
async def run():
    from playwright.async_api import async_playwright
    shots=f'{check.ROOT}/tools/shots'; errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None, args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':960,'height':540}); await ctx.add_init_script(f"try{{localStorage.setItem('tl_quality4', JSON.stringify('{check.Q}'))}}catch(e){{}}")
        pg=await ctx.new_page(); pg.set_default_timeout(300000); pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true', timeout=300000)
        await pg.evaluate("(async()=>{ const g=window.__game; g.settings.map='a1'; g.settings.mode='base'; await g.startCampaign(); g.player.invuln=9999; })()")
        await pg.wait_for_timeout(6000)
        for i in range(int(os.environ.get("NL","4"))):
            await pg.evaluate(f"""(()=>{{const g=window.__game,L=g.lightCells[{i}%g.lightCells.length]; if(!L) return;
              g.enemies.forEach(e=>{{e.cool=99;}}); const p=g.player; p.invuln=9999; p.pos.set(L.x+2.6,0,L.z+2.6); p.yaw=Math.atan2(2.6,2.6); p.pitch=-0.55; }})()""")
            for on in (1,0):
                await pg.evaluate(f"window.__game.BAKE_U.rainU.value.x={on}")
                await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{shots}/rain_{check.Q}_{i}_{"on" if on else "off"}.png')
            await pg.evaluate("window.__game.BAKE_U.rainU.value.x=1")
        await b.close()
    return errs
check.prep(); pr=check.server()
try: print('errors', asyncio.run(run()))
finally: pr.terminate()

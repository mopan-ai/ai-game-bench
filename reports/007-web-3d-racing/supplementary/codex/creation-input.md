制作一个可在桌面浏览器中玩的单人 3D 赛车计时游戏，采用原创低多边形风格和跟随车辆的第三人称镜头。只需一条短的封闭环形赛道，支持键盘加速、刹车和左右转向；有清晰可见的赛道边界，车辆不能穿越边界抄近路。沿赛道设置至少三个可见的有序检查点，并显示当前检查点或进度；只有按顺序通过所有检查点，再正确方向越过起终点线，才算完成一圈。显示本局计时，完赛后显示并停止最终用时；可以重新开始，恢复车辆位置、计时和检查点进度。请显示操作说明；在手机尺寸窗口中也能看清主要界面，但不要求触屏操作。不需要 AI 对手、联网、登录或多人模式。


Local development delivery contract (the game requirements above are unchanged):

Build the requested game in this initially empty /workspace/game directory.
Use any browser-compatible engine or libraries. Deliver a static playable build
with /workspace/game/dist/index.html and all of its runtime dependencies in dist,
so it can be served by a local HTTP server without a build step or external CDN.
Keep source and startup notes in this workspace. Package installation during
creation is allowed. Do not call external generation services or paid asset APIs,
publish/deploy anything, or read account credentials. Implement the game directly;
choose sensible defaults if a detail is unspecified. Finish with a short delivery
message after your own checks. There is no prior project or task-specific skill.


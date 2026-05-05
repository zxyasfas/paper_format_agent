"""
Paper Format Agent - 精美交互界面
现代化的 GUI 界面，支持拖拽、进度显示和可视化报告
"""

from __future__ import annotations

import json
import os
import sys
import threading
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.font import Font

try:
    import tkinter as tk
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    import tkinter as tk
    DRAG_DROP_AVAILABLE = False

from docx import Document

from .calibration import calibrate_from_labels
from .engines import run_postprocess_engine
from .pipeline import run_pipeline
from .rules import extract_rules_from_text
from .scorer import save_reports, score_document


class ModernTheme:
    """现代化主题配色"""
    PRIMARY = "#2196F3"  # Material Blue
    PRIMARY_DARK = "#1976D2"
    PRIMARY_LIGHT = "#BBDEFB"
    SUCCESS = "#4CAF50"  # Green
    WARNING = "#FF9800"  # Orange
    ERROR = "#F44336"  # Red
    BACKGROUND = "#FAFAFA"
    SURFACE = "#FFFFFF"
    ON_SURFACE = "#212121"
    ON_PRIMARY = "#FFFFFF"
    DIVIDER = "#E0E0E0"


class RoundedButton(tk.Canvas):
    """圆角按钮组件"""
    def __init__(self, parent, text, command=None, bg=ModernTheme.PRIMARY, 
                 fg=ModernTheme.ON_PRIMARY, width=120, height=40, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], 
                        highlightthickness=0, cursor="hand2", **kwargs)
        self.command = command
        self.bg = bg
        self.fg = fg
        self.text = text
        self.radius = 20
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
        self.draw_button()
        
    def draw_button(self, hover=False):
        self.delete("all")
        color = self._lighten_color(self.bg) if hover else self.bg
        
        # 绘制圆角矩形
        self.create_rounded_rect(2, 2, self.winfo_reqwidth()-2, self.winfo_reqheight()-2, 
                                 self.radius, fill=color, outline="")
        
        # 文字
        self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2, 
                        text=self.text, fill=self.fg, font=("Microsoft YaHei", 11, "bold"))
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, 
                  x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2, 
                  x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _lighten_color(self, color):
        """稍微提亮颜色用于悬停效果"""
        return ModernTheme.PRIMARY_DARK if color == ModernTheme.PRIMARY else color
    
    def on_enter(self, event):
        self.draw_button(hover=True)
    
    def on_leave(self, event):
        self.draw_button(hover=False)
    
    def on_click(self, event):
        if self.command:
            self.command()


class FileDropZone(tk.Frame):
    """文件拖拽区域组件"""
    def __init__(self, parent, title, file_types, callback, **kwargs):
        super().__init__(parent, bg=ModernTheme.SURFACE, **kwargs)
        self.callback = callback
        self.file_types = file_types
        
        # 边框容器
        self.container = tk.Frame(self, bg=ModernTheme.PRIMARY_LIGHT, padx=2, pady=2)
        self.container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 内部区域
        self.inner = tk.Frame(self.container, bg=ModernTheme.SURFACE, padx=20, pady=20)
        self.inner.pack(fill="both", expand=True)
        
        # 图标
        self.icon_label = tk.Label(self.inner, text="📄", font=("Segoe UI Emoji", 48),
                                   bg=ModernTheme.SURFACE, fg=ModernTheme.PRIMARY)
        self.icon_label.pack(pady=10)
        
        # 标题
        self.title_label = tk.Label(self.inner, text=title, font=("Microsoft YaHei", 12, "bold"),
                                    bg=ModernTheme.SURFACE, fg=ModernTheme.ON_SURFACE)
        self.title_label.pack()
        
        # 说明文字
        self.desc_label = tk.Label(self.inner, text=f"支持格式: {', '.join(file_types)}",
                                   font=("Microsoft YaHei", 9),
                                   bg=ModernTheme.SURFACE, fg="#757575")
        self.desc_label.pack(pady=5)
        
        # 文件名显示
        self.file_label = tk.Label(self.inner, text="点击选择文件或拖拽到此处",
                                   font=("Microsoft YaHei", 10),
                                   bg=ModernTheme.SURFACE, fg=ModernTheme.PRIMARY,
                                   wraplength=250)
        self.file_label.pack(pady=10)
        
        # 选择按钮
        self.select_btn = tk.Label(self.inner, text="选择文件", font=("Microsoft YaHei", 10),
                                   bg=ModernTheme.PRIMARY, fg=ModernTheme.ON_PRIMARY,
                                   padx=20, pady=5, cursor="hand2")
        self.select_btn.pack(pady=10)
        self.select_btn.bind("<Enter>", lambda e: self.select_btn.configure(bg=ModernTheme.PRIMARY_DARK))
        self.select_btn.bind("<Leave>", lambda e: self.select_btn.configure(bg=ModernTheme.PRIMARY))
        self.select_btn.bind("<Button-1>", self.on_select)
        
        self.file_path = None
        
        # 绑定拖拽事件
        if DRAG_DROP_AVAILABLE:
            self.inner.drop_target_register(DND_FILES)
            self.inner.dnd_bind('<<Drop>>', self.on_drop)
    
    def on_drop(self, event):
        """处理拖拽文件"""
        file_path = event.data.strip('{}"')
        if file_path and Path(file_path).suffix.lower() in self.file_types:
            self.set_file(file_path)
        else:
            messagebox.showwarning("格式不支持", f"请上传 {', '.join(self.file_types)} 格式的文件")
    
    def on_select(self, event=None):
        """点击选择文件"""
        file_path = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[(f"{ext.upper()} 文件", f"*{ext}") for ext in self.file_types] + [("所有文件", "*.*")]
        )
        if file_path:
            self.set_file(file_path)
    
    def set_file(self, file_path):
        """设置文件路径"""
        self.file_path = file_path
        file_name = Path(file_path).name
        self.file_label.configure(text=file_name, fg=ModernTheme.SUCCESS)
        self.icon_label.configure(text="✅", fg=ModernTheme.SUCCESS)
        if self.callback:
            self.callback(file_path)
    
    def get_file(self):
        return self.file_path
    
    def clear(self):
        self.file_path = None
        self.file_label.configure(text="点击选择文件或拖拽到此处", fg=ModernTheme.PRIMARY)
        self.icon_label.configure(text="📄", fg=ModernTheme.PRIMARY)


class ProgressBar(tk.Canvas):
    """自定义进度条"""
    def __init__(self, parent, width=400, height=8, **kwargs):
        super().__init__(parent, width=width, height=height, bg=ModernTheme.DIVIDER,
                        highlightthickness=0, **kwargs)
        self.progress = 0
        self.width = width
        self.height = height
        self.draw_progress()
    
    def draw_progress(self):
        self.delete("all")
        # 背景
        self.create_rectangle(0, 0, self.width, self.height, fill=ModernTheme.DIVIDER, outline="")
        # 进度
        if self.progress > 0:
            progress_width = int(self.width * self.progress / 100)
            self.create_rectangle(0, 0, progress_width, self.height, 
                                fill=ModernTheme.PRIMARY, outline="")
    
    def set_progress(self, value):
        self.progress = max(0, min(100, value))
        self.draw_progress()
        self.update()


class PaperFormatGUI:
    """主应用程序"""
    def __init__(self, root):
        self.root = root
        self.root.title("📚 论文格式智能排版工具")
        self.root.geometry("900x700")
        self.root.configure(bg=ModernTheme.BACKGROUND)
        self.root.minsize(800, 600)
        
        # 设置窗口居中
        self.center_window()
        
        self.format_file = None
        self.paper_file = None
        self.is_running = False
        
        self.create_widgets()
    
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = 900
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建界面组件"""
        # 顶部标题栏
        self.header = tk.Frame(self.root, bg=ModernTheme.PRIMARY, height=80)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        
        # Logo 和标题
        self.logo_label = tk.Label(self.header, text="🎓", font=("Segoe UI Emoji", 36),
                                   bg=ModernTheme.PRIMARY, fg=ModernTheme.ON_PRIMARY)
        self.logo_label.pack(side="left", padx=30, pady=10)
        
        self.title_frame = tk.Frame(self.header, bg=ModernTheme.PRIMARY)
        self.title_frame.pack(side="left", fill="y", pady=15)
        
        self.title_label = tk.Label(self.title_frame, text="论文格式智能排版工具",
                                    font=("Microsoft YaHei", 18, "bold"),
                                    bg=ModernTheme.PRIMARY, fg=ModernTheme.ON_PRIMARY)
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = tk.Label(self.title_frame, text="AI 驱动的毕业论文自动格式化系统",
                                       font=("Microsoft YaHei", 10),
                                       bg=ModernTheme.PRIMARY, fg=ModernTheme.PRIMARY_LIGHT)
        self.subtitle_label.pack(anchor="w")
        
        # 主内容区
        self.main_frame = tk.Frame(self.root, bg=ModernTheme.BACKGROUND)
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # 文件选择区域
        self.files_frame = tk.Frame(self.main_frame, bg=ModernTheme.BACKGROUND)
        self.files_frame.pack(fill="both", expand=True)
        
        # 左侧：格式规范文件
        self.format_frame = tk.LabelFrame(self.files_frame, text="📋 格式规范文件",
                                          font=("Microsoft YaHei", 11, "bold"),
                                          bg=ModernTheme.BACKGROUND, fg=ModernTheme.ON_SURFACE,
                                          padx=10, pady=10)
        self.format_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        self.format_drop = FileDropZone(self.format_frame, "上传格式规范文件",
                                        [".docx", ".doc", ".txt"],
                                        self.on_format_selected)
        self.format_drop.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 右侧：论文文件
        self.paper_frame = tk.LabelFrame(self.files_frame, text="📝 论文文件",
                                         font=("Microsoft YaHei", 11, "bold"),
                                         bg=ModernTheme.BACKGROUND, fg=ModernTheme.ON_SURFACE,
                                         padx=10, pady=10)
        self.paper_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        self.paper_drop = FileDropZone(self.paper_frame, "上传论文文件",
                                       [".docx"],
                                       self.on_paper_selected)
        self.paper_drop.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 选项区域
        self.options_frame = tk.LabelFrame(self.main_frame, text="⚙️ 排版选项",
                                           font=("Microsoft YaHei", 11, "bold"),
                                           bg=ModernTheme.BACKGROUND, fg=ModernTheme.ON_SURFACE,
                                           padx=15, pady=10)
        self.options_frame.pack(fill="x", pady=15)
        
        # 严格模式选项
        self.strict_var = tk.BooleanVar(value=False)
        self.strict_check = tk.Checkbutton(self.options_frame, text="严格模式（按模板必需项校验）",
                                           variable=self.strict_var,
                                           font=("Microsoft YaHei", 10),
                                           bg=ModernTheme.BACKGROUND, fg=ModernTheme.ON_SURFACE,
                                           selectcolor=ModernTheme.SURFACE,
                                           activebackground=ModernTheme.BACKGROUND)
        self.strict_check.pack(anchor="w", pady=3)
        
        # 输出明细选项
        self.marker_var = tk.BooleanVar(value=True)
        self.marker_check = tk.Checkbutton(self.options_frame, text="输出段落类型识别明细",
                                           variable=self.marker_var,
                                           font=("Microsoft YaHei", 10),
                                           bg=ModernTheme.BACKGROUND, fg=ModernTheme.ON_SURFACE,
                                           selectcolor=ModernTheme.SURFACE,
                                           activebackground=ModernTheme.BACKGROUND)
        self.marker_check.pack(anchor="w", pady=3)
        
        # 进度区域
        self.progress_frame = tk.Frame(self.main_frame, bg=ModernTheme.BACKGROUND)
        self.progress_frame.pack(fill="x", pady=15)
        
        self.progress_label = tk.Label(self.progress_frame, text="就绪",
                                       font=("Microsoft YaHei", 10),
                                       bg=ModernTheme.BACKGROUND, fg=ModernTheme.ON_SURFACE)
        self.progress_label.pack(anchor="w")
        
        self.progress_bar = ProgressBar(self.progress_frame, width=840)
        self.progress_bar.pack(fill="x", pady=5)
        
        # 操作按钮区域
        self.button_frame = tk.Frame(self.main_frame, bg=ModernTheme.BACKGROUND)
        self.button_frame.pack(fill="x", pady=10)
        
        # 开始按钮
        self.start_btn = RoundedButton(self.button_frame, "🚀 开始排版", 
                                       command=self.start_formatting,
                                       bg=ModernTheme.SUCCESS, width=150, height=45)
        self.start_btn.pack(side="left", padx=5)
        
        # 清除按钮
        self.clear_btn = RoundedButton(self.button_frame, "🔄 清除",
                                       command=self.clear_all,
                                       bg=ModernTheme.WARNING, width=120, height=45)
        self.clear_btn.pack(side="left", padx=5)
        
        # 查看报告按钮（初始禁用）
        self.report_btn = RoundedButton(self.button_frame, "📊 查看报告",
                                        command=self.open_report,
                                        bg=ModernTheme.PRIMARY, width=120, height=45)
        self.report_btn.pack(side="right", padx=5)
        
        # 输出目录按钮
        self.output_btn = RoundedButton(self.button_frame, "📁 输出目录",
                                        command=self.open_output_dir,
                                        bg=ModernTheme.PRIMARY, width=120, height=45)
        self.output_btn.pack(side="right", padx=5)
        
        # 状态栏
        self.status_bar = tk.Frame(self.root, bg=ModernTheme.SURFACE, height=30)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="就绪 | 请选择文件",
                                     font=("Microsoft YaHei", 9),
                                     bg=ModernTheme.SURFACE, fg="#757575")
        self.status_label.pack(side="left", padx=15, pady=5)
        
        self.output_path = Path.home() / "Documents" / "PaperFormatOutput"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.last_output_dir = None
        self.last_report_path = None
    
    def on_format_selected(self, file_path):
        """格式文件选择回调"""
        self.format_file = file_path
        self.update_status()
    
    def on_paper_selected(self, file_path):
        """论文文件选择回调"""
        self.paper_file = file_path
        self.update_status()
    
    def update_status(self):
        """更新状态栏"""
        if self.format_file and self.paper_file:
            self.status_label.configure(text="✅ 文件就绪，可以开始排版", fg=ModernTheme.SUCCESS)
        elif self.format_file:
            self.status_label.configure(text="⏳ 已选择格式规范，请选择论文文件", fg=ModernTheme.WARNING)
        elif self.paper_file:
            self.status_label.configure(text="⏳ 已选择论文文件，请选择格式规范", fg=ModernTheme.WARNING)
        else:
            self.status_label.configure(text="就绪 | 请选择文件", fg="#757575")
    
    def start_formatting(self):
        """开始排版"""
        if not self.format_file:
            messagebox.showwarning("缺少文件", "请先选择格式规范文件")
            return
        if not self.paper_file:
            messagebox.showwarning("缺少文件", "请先选择论文文件")
            return
        
        if self.is_running:
            return
        
        self.is_running = True
        self.progress_bar.set_progress(0)
        self.progress_label.configure(text="准备开始...", fg=ModernTheme.PRIMARY)
        
        # 在新线程中运行，避免界面卡顿
        thread = threading.Thread(target=self.run_formatting_process)
        thread.daemon = True
        thread.start()
    
    def run_formatting_process(self):
        """运行排版处理"""
        try:
            self.update_progress(5, "正在读取格式规范...")
            
            # 读取格式规范
            from .cli import read_format_text
            format_text = read_format_text(self.format_file)
            rules = extract_rules_from_text(format_text)
            
            self.update_progress(15, "正在分析论文结构...")
            
            # 创建输出目录
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            self.last_output_dir = self.output_path / f"output_{timestamp}"
            self.last_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存规则
            (self.last_output_dir / "format_rules.json").write_text(
                json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            
            self.update_progress(30, "正在执行格式修复...")
            
            # 运行排版流程
            marker_dump = self.last_output_dir / "marker_dump.json" if self.marker_var.get() else None
            output_docx = self.last_output_dir / "formatted_paper.docx"
            
            run_result = run_pipeline(
                self.paper_file, 
                output_docx, 
                rules, 
                write_marker_dump=marker_dump
            )
            
            (self.last_output_dir / "modify_log.json").write_text(
                json.dumps(run_result.logs, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            
            self.update_progress(60, "正在执行引擎后处理...")
            
            # 引擎后处理
            engine_report = run_postprocess_engine("auto", output_docx)
            (self.last_output_dir / "engine_report.json").write_text(
                json.dumps(engine_report, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            
            self.update_progress(80, "正在生成评分报告...")
            
            # 评分
            report = score_document(
                output_docx,
                rules,
                baseline_docx=self.paper_file,
                enforce_required_sections=self.strict_var.get(),
            )
            report["engine_report"] = engine_report
            report["removed_numpr_count"] = run_result.removed_numpr_count
            report["classification_confidence"] = run_result.classification_confidence
            
            self.last_report_path = self.last_output_dir / "format_report.html"
            save_reports(report, self.last_output_dir / "format_report.json", self.last_report_path)
            
            self.update_progress(100, "✅ 排版完成！")
            
            # 显示结果
            score = report["score"]
            chars = report["chars_no_space"]
            
            self.root.after(0, lambda: self.show_success_message(score, chars))
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error_message(str(e)))
        finally:
            self.is_running = False
    
    def update_progress(self, value, message):
        """更新进度（线程安全）"""
        self.root.after(0, lambda: self._update_progress_ui(value, message))
    
    def _update_progress_ui(self, value, message):
        """更新进度 UI"""
        self.progress_bar.set_progress(value)
        self.progress_label.configure(text=message, fg=ModernTheme.PRIMARY)
    
    def show_success_message(self, score, chars):
        """显示成功消息"""
        color = ModernTheme.SUCCESS if score >= 90 else ModernTheme.WARNING if score >= 60 else ModernTheme.ERROR
        emoji = "🎉" if score >= 90 else "👍" if score >= 60 else "⚠️"
        
        message = f"{emoji} 排版完成！\n\n"
        message += f"📊 格式评分: {score:.1f} 分\n"
        message += f"📝 论文字数: {chars:,} 字符\n\n"
        message += f"📁 输出目录: {self.last_output_dir}"
        
        self.status_label.configure(text=f"✅ 排版完成 | 评分: {score:.1f} 分", fg=color)
        
        if messagebox.askyesno("排版完成", message + "\n\n是否立即查看报告？"):
            self.open_report()
    
    def show_error_message(self, error):
        """显示错误消息"""
        self.progress_label.configure(text=f"❌ 出错: {error}", fg=ModernTheme.ERROR)
        self.status_label.configure(text="❌ 排版失败", fg=ModernTheme.ERROR)
        self.progress_bar.set_progress(0)
        messagebox.showerror("排版失败", f"处理过程中出现错误:\n{error}")
    
    def clear_all(self):
        """清除所有选择"""
        self.format_drop.clear()
        self.paper_drop.clear()
        self.format_file = None
        self.paper_file = None
        self.progress_bar.set_progress(0)
        self.progress_label.configure(text="就绪", fg=ModernTheme.ON_SURFACE)
        self.update_status()
        self.last_output_dir = None
        self.last_report_path = None
    
    def open_report(self):
        """打开报告"""
        if self.last_report_path and self.last_report_path.exists():
            webbrowser.open(f"file:///{self.last_report_path}")
        else:
            messagebox.showinfo("提示", "还没有生成报告，请先运行排版")
    
    def open_output_dir(self):
        """打开输出目录"""
        if self.last_output_dir and self.last_output_dir.exists():
            os.startfile(self.last_output_dir)
        else:
            os.startfile(self.output_path)


def main():
    """主入口"""
    if DRAG_DROP_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    app = PaperFormatGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

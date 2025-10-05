import argparse
import queue
import threading
import time
import speech_recognition as sr
from deep_translator import GoogleTranslator

try:
    import tkinter as tk
    from tkinter.scrolledtext import ScrolledText
    from tkinter import filedialog, messagebox, ttk, font
except Exception:
    tk = None
    ScrolledText = None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", "-s", default="sl")
    parser.add_argument("--target", "-t", default="en")
    args = parser.parse_args()

    source_lang = args.source
    target_lang = args.target

    recognizer = sr.Recognizer()
    tx_queue = queue.Queue()
    ui_queue = queue.Queue()

    target_holder = {"value": target_lang}

    def translator_worker():
        while True:
            item = tx_queue.get()
            if item is None:
                break
            timestamp, text = item
            current_target = target_holder.get("value", target_lang)
            try:
                translator = GoogleTranslator(source=source_lang, target=current_target)
                translated = translator.translate(text)
            except Exception as err:
                print("Translation error:", err)
                translated = ""

            print(f"[{timestamp:.1f}] {source_lang}: {text}")
            print(f"[{timestamp:.1f}] {current_target}: {translated}\n")

            try:
                ui_queue.put((timestamp, text, translated))
            except Exception:
                pass

            tx_queue.task_done()

    worker = threading.Thread(target=translator_worker, daemon=True)
    worker.start()

    mic = sr.Microphone()
    print(f"Starting translator {source_lang} -> {target_lang}")
    with mic as src:
        recognizer.adjust_for_ambient_noise(src, duration=0.8)

    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.3
    try:
        recognizer.non_speaking_duration = 0.1
    except Exception:
        pass

    def callback(recognizer_obj, audio_blob):
        try:
            text = recognizer_obj.recognize_google(audio_blob, language=source_lang)
            tx_queue.put((time.time(), text))
        except sr.UnknownValueError:
            return
        except sr.RequestError as err:
            print("Speech recognition request failed:", err)

    stop_listener = [None]
    listening = {"running": False}

    def start_background_listen():
        if stop_listener[0] is None:
            try:
                stopper = recognizer.listen_in_background(mic, callback, phrase_time_limit=None)
                stop_listener[0] = stopper
                listening["running"] = True
                return True
            except Exception as err:
                print("Failed to start listening:", err)
                return False
        return True

    def stop_background_listen():
        if stop_listener[0]:
            try:
                stop_listener[0](wait_for_stop=False)
            except Exception:
                pass
            stop_listener[0] = None
        listening["running"] = False

    if tk and ScrolledText:
        root = tk.Tk()
        root.title(f"Translator: {source_lang} → {target_holder['value']}")

        start_background_listen()

        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        controls = ttk.Frame(root, padding=(6, 6))
        controls.pack(fill=tk.X)

        start_stop_btn = ttk.Button(controls, text="Stop")
        start_stop_btn.pack(side=tk.LEFT, padx=6)

        lang_var = tk.StringVar(value=target_holder["value"])
        lang_dropdown = ttk.Combobox(controls, textvariable=lang_var, values=("sr", "en"), width=6, state="readonly")
        lang_dropdown.pack(side=tk.LEFT, padx=6)

        save_btn = ttk.Button(controls, text="Save")
        save_btn.pack(side=tk.LEFT, padx=6)

        ttk.Label(controls, text="Transparency").pack(side=tk.LEFT, padx=(20, 4))
        trans_var = tk.DoubleVar(value=1.0)
        trans_scale = ttk.Scale(controls, from_=0.3, to=1.0, orient=tk.HORIZONTAL, variable=trans_var)
        trans_scale.pack(side=tk.LEFT, padx=4)

        def on_trans(*_):
            try:
                root.attributes("-alpha", float(trans_var.get()))
            except Exception:
                pass

        trans_var.trace_add("write", on_trans)

        paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=1)

        left_frame = tk.Frame(paned)
        right_frame = tk.Frame(paned)
        paned.add(left_frame)
        paned.add(right_frame)

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=10)

        ttk.Label(left_frame, text=f"Source ({source_lang})", anchor="w").pack(fill=tk.X, padx=4, pady=(4, 0))
        left_text = ScrolledText(left_frame, wrap=tk.WORD, height=20, width=50)
        left_text.pack(fill=tk.BOTH, expand=1, padx=4, pady=4)
        left_text.configure(state=tk.DISABLED, font=default_font)

        ttk.Label(right_frame, text=f"Translation ({target_holder['value']})", anchor="w").pack(fill=tk.X, padx=4, pady=(4, 0))
        right_text = ScrolledText(right_frame, wrap=tk.WORD, height=20, width=50)
        right_text.pack(fill=tk.BOTH, expand=1, padx=4, pady=4)
        right_text.configure(state=tk.DISABLED, font=default_font)

        def widget_is_at_bottom(w, slack=3):
            last_visible = w.index(f"@0,{w.winfo_height()}")
            last_index = w.index("end-1c")
            try:
                return int(last_index.split('.')[0]) - int(last_visible.split('.')[0]) <= slack
            except Exception:
                return True

        def poll_ui():
            try:
                while True:
                    item = ui_queue.get_nowait()
                    if not item:
                        continue
                    ts, s_text, t_text = item
                    left_bottom = widget_is_at_bottom(left_text)
                    left_text.configure(state=tk.NORMAL)
                    left_text.insert(tk.END, f"[{ts:.1f}] {s_text}\n")
                    if left_bottom:
                        left_text.see(tk.END)
                    left_text.configure(state=tk.DISABLED)

                    right_bottom = widget_is_at_bottom(right_text)
                    right_text.configure(state=tk.NORMAL)
                    right_text.insert(tk.END, f"[{ts:.1f}] {t_text}\n")
                    if right_bottom:
                        right_text.see(tk.END)
                    right_text.configure(state=tk.DISABLED)

                    ui_queue.task_done()
            except queue.Empty:
                pass
            root.after(100, poll_ui)

        def toggle_listen():
            if listening.get("running"):
                stop_background_listen()
                start_stop_btn.configure(text="Start")
            else:
                ok = start_background_listen()
                if ok:
                    start_stop_btn.configure(text="Stop")

        def on_lang_change(*_):
            new = lang_var.get()
            target_holder["value"] = new
            right_text_label = f"Translation ({new})"
            # find and update the right label
            for child in right_frame.winfo_children():
                if isinstance(child, ttk.Label):
                    child.configure(text=right_text_label)
                    break

        def save_transcript():
            try:
                path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text', '*.txt')])
                if not path:
                    return
                left_text.configure(state=tk.NORMAL)
                left_content = left_text.get('1.0', tk.END).strip()
                left_text.configure(state=tk.DISABLED)

                right_text.configure(state=tk.NORMAL)
                right_content = right_text.get('1.0', tk.END).strip()
                right_text.configure(state=tk.DISABLED)

                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(f"Source ({source_lang})\n")
                    fh.write(left_content + "\n\n")
                    fh.write(f"Translation ({target_holder.get('value')})\n")
                    fh.write(right_content + "\n")

                messagebox.showinfo('Saved', f'Saved transcript to {path}')
            except Exception as err:
                messagebox.showerror('Error', f'Failed to save: {err}')

        start_stop_btn.configure(command=toggle_listen)
        lang_var.trace_add('write', on_lang_change)
        save_btn.configure(command=save_transcript)

        def on_close():
            print("Stopping...")
            try:
                stop_background_listen()
            except Exception:
                pass
            tx_queue.put(None)
            worker.join(timeout=2)
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_close)
        root.after(100, poll_ui)
        try:
            root.mainloop()
        except KeyboardInterrupt:
            on_close()
    else:
        try:
            while True:
                time.sleep(0)
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            try:
                stop_background_listen()
            except Exception:
                pass
            tx_queue.put(None)
            worker.join(timeout=0)


if __name__ == "__main__":
    main()
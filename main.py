import tkinter as tk
from tkinter import messagebox

from seka_game import MAX_EXCHANGES, SekaGame, hand_hint, hand_score


class SekaApp:
    BACKGROUND = "#123b32"
    PANEL = "#1c5144"
    TEXT = "#fff8e8"
    ACCENT = "#f1c75b"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Seka — botlarga qarshi")
        self.root.geometry("850x680")
        self.root.minsize(700, 580)
        self.root.configure(bg=self.BACKGROUND)
        self.game = SekaGame()
        self.allow_exchanges = True
        self.selected_card: int | None = None
        self.status = tk.StringVar()
        self.hint = tk.StringVar()

        self.menu_frame = tk.Frame(root, bg=self.BACKGROUND)
        tk.Label(
            self.menu_frame, text="SEKA", font=("Segoe UI", 34, "bold"),
            fg=self.ACCENT, bg=self.BACKGROUND,
        ).pack(pady=(75, 8))
        tk.Label(
            self.menu_frame,
            text="O‘yin turini tanlang\n3 ta botga qarshi, internetsiz",
            font=("Segoe UI", 14), fg=self.TEXT, bg=self.BACKGROUND,
            justify="center",
        ).pack(pady=(0, 28))
        tk.Button(
            self.menu_frame, text="1-variant: karta almashtirish mumkin",
            font=("Segoe UI", 12, "bold"), width=38, height=2,
            command=lambda: self.start_game(allow_exchanges=True),
        ).pack(pady=8)
        tk.Button(
            self.menu_frame, text="2-variant: karta almashtirish mumkin emas",
            font=("Segoe UI", 12, "bold"), width=38, height=2,
            command=lambda: self.start_game(allow_exchanges=False),
        ).pack(pady=8)
        tk.Label(
            self.menu_frame,
            text="1-variantda navbat bilan kartani almashtirish mumkin.\n"
            "2-variantda tarqatilgan 3 ta karta bilan o‘ynaladi.",
            font=("Segoe UI", 10), fg="#d5e9dc", bg=self.BACKGROUND,
            justify="center",
        ).pack(pady=20)
        self.menu_frame.pack(fill="both", expand=True)
        self.game_frame = tk.Frame(root, bg=self.BACKGROUND)

        tk.Label(
            self.game_frame, text="SEKA", font=("Segoe UI", 30, "bold"),
            fg=self.ACCENT, bg=self.BACKGROUND,
        ).pack(pady=(12, 0))
        tk.Label(
            self.game_frame, text="Internet va LANsiz — 3 ta botga qarshi o‘rganing",
            font=("Segoe UI", 11), fg=self.TEXT, bg=self.BACKGROUND,
        ).pack(pady=(0, 12))

        self.table = tk.Frame(self.game_frame, bg=self.PANEL, padx=18, pady=12)
        self.table.pack(fill="both", expand=True, padx=20)
        self.bot_labels = []
        for index in range(3):
            label = tk.Label(
                self.table, font=("Segoe UI", 11), fg=self.TEXT,
                bg=self.PANEL, justify="left", anchor="w",
            )
            label.pack(fill="x", pady=4)
            self.bot_labels.append(label)

        tk.Label(
            self.table, textvariable=self.status, font=("Segoe UI", 11, "bold"),
            fg=self.ACCENT, bg=self.PANEL, anchor="w",
        ).pack(fill="x", pady=(8, 4))
        self.hand_frame = tk.Frame(self.table, bg=self.PANEL)
        self.hand_frame.pack(pady=8)
        self.card_buttons = []
        for index in range(3):
            button = tk.Button(
                self.hand_frame, width=8, height=3, font=("Segoe UI", 16, "bold"),
                command=lambda card_index=index: self.select_card(card_index),
                relief="raised", bd=3,
            )
            button.grid(row=0, column=index, padx=7)
            self.card_buttons.append(button)

        self.score_label = tk.Label(
            self.table, font=("Segoe UI", 11), fg=self.TEXT, bg=self.PANEL,
        )
        self.score_label.pack()
        self.hint_label = tk.Label(
            self.table, textvariable=self.hint, font=("Segoe UI", 10),
            fg="#d5e9dc", bg=self.PANEL, wraplength=740,
        )
        self.hint_label.pack(pady=(3, 5))

        controls = tk.Frame(self.game_frame, bg=self.BACKGROUND)
        controls.pack(pady=12)
        self.exchange_button = tk.Button(
            controls, text="Almashtirish", width=16, command=self.exchange,
        )
        self.exchange_button.grid(row=0, column=0, padx=5)
        self.stand_button = tk.Button(
            controls, text="Pas / to‘xtash", width=16, command=self.stand,
        )
        self.stand_button.grid(row=0, column=1, padx=5)
        tk.Button(
            controls, text="Maslahat", width=12, command=self.show_hint,
        ).grid(row=0, column=2, padx=5)
        self.new_button = tk.Button(
            controls, text="Yangi raund", width=14, command=self.new_round,
        )
        self.new_button.grid(row=0, column=3, padx=5)
        tk.Button(
            controls, text="Bosh menyu", width=14, command=self.show_menu,
        ).grid(row=0, column=4, padx=5)

        self.rules_label = tk.Label(
            self.game_frame, font=("Segoe UI", 9), fg=self.TEXT,
            bg=self.BACKGROUND, wraplength=810, justify="left",
        )
        self.rules_label.pack(fill="x", padx=25, pady=(0, 12))

    def start_game(self, allow_exchanges: bool):
        self.allow_exchanges = allow_exchanges
        self.game = SekaGame(allow_exchanges=allow_exchanges)
        self.menu_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)
        self.rules_label.config(text=self._rules_text())
        self.new_round()

    def show_menu(self):
        self.game_frame.pack_forget()
        self.menu_frame.pack(fill="both", expand=True)

    def _rules_text(self):
        rules = (
            "Qoidalar: 36 kartali koloda (6 dan tuzgacha), har kim 3 karta oladi. "
            "Faqat bir xil rangdagi kartalar ochkosi qo‘shiladi: 6–10 o‘z qiymatida, "
            "J/Q/K = 10, A = 11. Eng yuqori bitta rang yig‘indisi — qo‘l ochkosi. "
        )
        if self.allow_exchanges:
            rules += (
                "Navbatda bitta kartani almashtiring yoki to‘xtang; "
                "ko‘pi bilan 3 marta. "
            )
        else:
            rules += "Kartalar almashtirilmaydi; tarqatilgan 3 karta bilan o‘ynang. "
        return rules + "Raund oxirida eng ko‘p ochko yutadi. Garovsiz variant."

    def new_round(self):
        self.game.new_round()
        self.selected_card = None
        if self.allow_exchanges:
            self.hint.set("Kartani tanlang va almashtiring yoki ‘Maslahat’ni bosing.")
        else:
            self.hint.set("Kartalarni ko‘rib chiqing, so‘ng ‘Natijani ko‘rish’ni bosing.")
        self.refresh()

    def select_card(self, index):
        if self.game.round_over or not self.game.current_player.is_human:
            return
        self.selected_card = index
        self.refresh()

    def exchange(self):
        if self.selected_card is None:
            messagebox.showinfo("Karta tanlanmagan", "Almashtirish uchun kartangizni tanlang.")
            return
        try:
            self.game.exchange(self.selected_card)
        except ValueError as error:
            messagebox.showinfo("Almashtirish mumkin emas", str(error))
            return
        self.selected_card = None
        messages = self.game.play_bots()
        self.hint.set("Siz kartani almashtirdingiz. " + " ".join(messages))
        self.finish_or_refresh()

    def stand(self):
        if self.game.round_over or not self.game.current_player.is_human:
            return
        self.game.stand()
        messages = self.game.play_bots()
        self.selected_card = None
        self.hint.set("Siz to‘xtadingiz. " + " ".join(messages))
        self.finish_or_refresh()

    def show_hint(self):
        if not self.game.round_over:
            player = self.game.players[0]
            hint = f"{hand_hint(player.cards)} Qo‘l ochkosi: {hand_score(player.cards)}."
            if self.allow_exchanges:
                hint += f" Almashtirish: {player.exchanges}/{MAX_EXCHANGES}."
            self.hint.set(hint)

    def finish_or_refresh(self):
        self.refresh()
        if self.game.round_over:
            winner = self.game.winner
            self.hint.set(
                f"Raund tugadi. G‘olib: {winner.name} "
                f"({hand_score(winner.cards)} ochko). Kartalarni ko‘rib, "
                "ranglar bo‘yicha ochkoni solishtiring."
            )
            self.refresh()

    def refresh(self):
        for index, (label, player) in enumerate(zip(self.bot_labels, self.game.players[1:])):
            if self.game.round_over:
                details = "  ".join(str(card) for card in player.cards)
                label.config(text=f"{player.name}: {details} — {hand_score(player.cards)} ochko")
            else:
                state = "to‘xtadi" if player.stood else "o‘ynayapti"
                label.config(text=f"{player.name}: 🂠 🂠 🂠   ({state})")

        human = self.game.players[0]
        for index, (button, card) in enumerate(zip(self.card_buttons, human.cards)):
            button.config(
                text=str(card),
                bg="#fff8e8" if index == self.selected_card else "white",
                fg="#b22b2b" if card.suit in ("♥", "♦") else "#222222",
                state="normal" if self._human_can_exchange() else "disabled",
            )
        self.score_label.config(
            text=(
                f"Sizning ochko: {hand_score(human.cards)}"
                + (
                    f"    Almashtirish: {human.exchanges}/{MAX_EXCHANGES}"
                    if self.allow_exchanges else "    Almashtirish: yo‘q"
                )
                + f"    Koloda: {len(self.game.deck)}"
            )
        )
        if self.game.round_over:
            self.status.set("Raund tugadi — yangi raund boshlashingiz mumkin.")
        elif self.game.current_player.is_human:
            self.status.set("Sizning navbatingiz.")
        else:
            self.status.set(f"{self.game.current_player.name} yurmoqda...")
        can_exchange = self._human_can_exchange()
        self.exchange_button.config(
            state="normal" if can_exchange and self.selected_card is not None else "disabled"
        )
        self.stand_button.config(
            state="normal" if self._human_can_stand() else "disabled"
        )
        self.stand_button.config(
            text="Natijani ko‘rish" if not self.allow_exchanges else "Pas / to‘xtash"
        )
        self.new_button.config(state="normal" if self.game.round_over else "disabled")

    def _human_can_exchange(self):
        if self.game.round_over or not self.game.current_player.is_human:
            return False
        human = self.game.players[0]
        return not human.stood and human.exchanges < MAX_EXCHANGES and bool(self.game.deck)

    def _human_can_stand(self):
        if self.game.round_over or not self.game.current_player.is_human:
            return False
        return not self.game.players[0].stood


def main():
    root = tk.Tk()
    SekaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

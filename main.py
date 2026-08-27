import pygame
import sys
import random
from datetime import datetime, timedelta

# Pygame Setup
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Daily Life Simulator")
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GREEN = (50, 205, 50)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)
CYAN = (0, 255, 255)
PURPLE = (147, 112, 219)
ORANGE = (255, 165, 0)

# Fonts
try:
    font_sm = pygame.font.SysFont("Arial", 16)
    font_md = pygame.font.SysFont("Arial", 24)
    font_lg = pygame.font.SysFont("Arial", 32)
except:
    font_sm = pygame.font.Font(None, 20)
    font_md = pygame.font.Font(None, 30)
    font_lg = pygame.font.Font(None, 40)

# --- Classes ---
class Button:
    def __init__(self, x, y, w, h, text, color, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        color = DARK_GRAY if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)

        text_surf = font_md.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos) and self.action:
            self.action()

class Player:
    def __init__(self):
        self.money = 1000000 # VNĐ
        self.diamonds = 0
        self.debt = 0

        # Stats (0 -> 100)
        self.health = 100
        self.hunger = 100
        self.thirst = 100

        # Mood: "Vui", "Bình thường", "Buồn"
        self.mood = "Bình thường"

class Game:
    def __init__(self):
        self.player = Player()
        # Time logic: Start at day 1, 08:00
        self.game_time = datetime(2024, 1, 1, 8, 0, 0)
        self.last_real_time = pygame.time.get_ticks()
        self.current_month = self.game_time.month
        self.current_day = self.game_time.day

        self.fast_forward = False
        self.fast_forward_target = None
        self.fast_forward_callback = None

        self.logs = ["Chào mừng bạn đến với Daily Life Simulator!"]
        self.buttons = self._create_buttons()

    def add_log(self, msg):
        self.logs.insert(0, f"[{self.game_time.strftime('%H:%M')}] {msg}")
        if len(self.logs) > 10:
            self.logs.pop()

    def start_fast_forward(self, hours, callback=None):
        if self.fast_forward:
            return
        self.fast_forward = True
        self.fast_forward_target = self.game_time + timedelta(hours=hours)
        self.fast_forward_callback = callback
        self.add_log(f"Bắt đầu tua nhanh {hours} giờ...")

    def action_work(self):
        def on_finish():
            salary = 500000
            self.player.money += salary
            self.player.hunger = max(0, self.player.hunger - 30)
            self.player.thirst = max(0, self.player.thirst - 30)
            self.player.mood = "Bình thường"
            self.add_log(f"Làm việc xong. Nhận {salary:,} VNĐ.")
        self.start_fast_forward(8, on_finish)

    def action_eat(self):
        cost = 50000
        if self.player.money >= cost:
            self.player.money -= cost
            self.player.hunger = min(100, self.player.hunger + 40)
            self.add_log(f"Ăn xong (Tốn {cost:,} VNĐ). Hồi 40 Đói.")
        else:
            self.add_log("Không đủ tiền để ăn!")

    def action_drink(self):
        cost = 20000
        if self.player.money >= cost:
            self.player.money -= cost
            self.player.thirst = min(100, self.player.thirst + 40)
            self.add_log(f"Uống xong (Tốn {cost:,} VNĐ). Hồi 40 Khát.")
        else:
            self.add_log("Không đủ tiền để uống!")

    def action_sleep(self):
        def on_finish():
            self.player.health = min(100, self.player.health + 50)
            self.player.mood = "Vui"
            self.add_log("Ngủ dậy. Sức khỏe +50, Tâm trạng: Vui.")
        self.start_fast_forward(8, on_finish)

    def action_play(self):
        cost = 100000
        if self.player.money >= cost:
            def on_finish():
                self.player.money -= cost
                self.player.mood = "Vui"
                self.add_log(f"Đi chơi vui vẻ! (Tốn {cost:,} VNĐ)")
            self.start_fast_forward(2, on_finish)
        else:
            self.add_log("Không đủ tiền đi chơi!")

    def action_learn(self):
        def on_finish():
            self.player.hunger = max(0, self.player.hunger - 15)
            self.player.thirst = max(0, self.player.thirst - 15)
            self.player.mood = "Buồn" # Học mệt
            self.add_log("Học tập xong. Hơi mệt và buồn một chút.")
        self.start_fast_forward(3, on_finish)

    def _create_buttons(self):
        buttons = []
        btn_y = HEIGHT - 80
        btn_w, btn_h = 100, 40
        gap = 20

        actions = [
            ("Đi làm", YELLOW, self.action_work),
            ("Ăn", GREEN, self.action_eat),
            ("Uống", BLUE, self.action_drink),
            ("Ngủ", PURPLE, self.action_sleep),
            ("Giải trí", CYAN, self.action_play),
            ("Học tập", GRAY, self.action_learn),
            ("Đổi KC", CYAN, self.exchange_diamonds),
        ]

        start_x = (WIDTH - (len(actions) * btn_w + (len(actions) - 1) * gap)) // 2

        for i, (text, color, action) in enumerate(actions):
            x = start_x + i * (btn_w + gap)
            buttons.append(Button(x, btn_y, btn_w, btn_h, text, color, action))

        return buttons

    def draw_avatar_and_time(self, surface):
        # Avatar placeholder (Top Left)
        avatar_rect = pygame.Rect(20, 20, 80, 80)
        pygame.draw.rect(surface, GRAY, avatar_rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, avatar_rect, 2, border_radius=10)
        av_text = font_sm.render("Avatar", True, BLACK)
        surface.blit(av_text, av_text.get_rect(center=avatar_rect.center))

        # Date & Time below avatar
        time_str = self.game_time.strftime("%d/%m/%Y %H:%M")
        time_surf = font_md.render(time_str, True, BLACK)
        surface.blit(time_surf, (20, 110))

    def draw_money_and_stats(self, surface):
        # Top Right Money & Diamonds
        money_str = f"{self.player.money:,} VNĐ"
        diamond_str = f"Kim cương: {self.player.diamonds}"

        money_surf = font_lg.render(money_str, True, GREEN)
        money_rect = money_surf.get_rect(topright=(WIDTH - 20, 20))
        surface.blit(money_surf, money_rect)

        diamond_surf = font_md.render(diamond_str, True, CYAN)
        diamond_rect = diamond_surf.get_rect(topright=(WIDTH - 20, money_rect.bottom + 5))
        surface.blit(diamond_surf, diamond_rect)

        # Stats bars below money
        stat_w = 200
        stat_h = 20
        stat_x = WIDTH - 220
        stat_y = diamond_rect.bottom + 20

        stats = [
            ("Sức khoẻ", self.player.health, RED),
            ("Đói", self.player.hunger, ORANGE),
            ("Khát", self.player.thirst, BLUE)
        ]

        for name, value, color in stats:
            # Label
            label_surf = font_sm.render(name, True, BLACK)
            surface.blit(label_surf, (stat_x - 70, stat_y))
            # Background bar
            pygame.draw.rect(surface, DARK_GRAY, (stat_x, stat_y, stat_w, stat_h), border_radius=5)
            # Fill bar
            fill_w = max(0, min(stat_w, (value / 100.0) * stat_w))
            if fill_w > 0:
                pygame.draw.rect(surface, color, (stat_x, stat_y, fill_w, stat_h), border_radius=5)
            # Border
            pygame.draw.rect(surface, BLACK, (stat_x, stat_y, stat_w, stat_h), 2, border_radius=5)

            stat_y += 30

        # Mood
        mood_surf = font_md.render(f"Tâm trạng: {self.player.mood}", True, PURPLE)
        surface.blit(mood_surf, (stat_x, stat_y))

    def update(self):
        current_time = pygame.time.get_ticks()
        dt_ms = current_time - self.last_real_time
        self.last_real_time = current_time
        dt_sec = dt_ms / 1000.0

        # Normal time: 1 real sec = 1 game min
        # Fast forward: 2 real sec = 1 game hour = 60 game mins -> 1 real sec = 30 game mins
        multiplier = 30 if self.fast_forward else 1

        game_mins_to_add = dt_sec * multiplier
        self.game_time += timedelta(minutes=game_mins_to_add)

        # Update Stats based on time passed
        # Base decay: 100 points per 24 hours (1440 mins) => ~0.069 points per minute
        base_decay = 100 / 1440.0

        # Mood modifier
        modifier = 1.0
        if self.player.mood == "Buồn":
            modifier = 1.20 # +20%
        elif self.player.mood == "Vui":
            modifier = 0.85 # -15%

        decay_amount = base_decay * game_mins_to_add * modifier

        self.player.hunger = max(0, self.player.hunger - decay_amount)
        self.player.thirst = max(0, self.player.thirst - decay_amount)

        # Health decay if Hunger or Thirst is 0
        if self.player.hunger == 0 or self.player.thirst == 0:
            health_decay = (100 / 720.0) * game_mins_to_add # Dies in 12 hours if 0 hunger/thirst
            self.player.health = max(0, self.player.health - health_decay)

        # Health checks
        if self.player.health < 30 and not hasattr(self, 'health_warning_sent'):
            self.add_log("CẢNH BÁO: Sức khỏe dưới 30%, bạn nên đi khám!")
            self.health_warning_sent = True
        elif self.player.health >= 30 and hasattr(self, 'health_warning_sent'):
            del self.health_warning_sent

        if self.player.health == 0:
            self.hospitalize()

        if self.fast_forward and self.game_time >= self.fast_forward_target:
            self.game_time = self.fast_forward_target
            self.fast_forward = False
            if self.fast_forward_callback:
                self.fast_forward_callback()
            self.fast_forward_callback = None

        # Monthly bill
        if self.game_time.month != self.current_month:
            self.current_month = self.game_time.month
            self.handle_monthly_bill()

        if self.game_time.day != self.current_day:
            self.current_day = self.game_time.day
            self.trigger_random_event()
            self.check_achievements()

    def exchange_diamonds(self):
        if self.player.diamonds >= 10:
            self.player.diamonds -= 10
            self.player.money += 350000
            self.add_log("Đổi 10 Kim cương lấy 350,000 VNĐ thành công!")
        else:
            self.add_log("Không đủ 10 Kim cương để đổi tiền.")

    def trigger_random_event(self):
        # 30% chance for a random event each day
        if random.random() < 0.3:
            events = [
                ("Bạn nhặt được 50,000 VNĐ trên đường!", lambda: setattr(self.player, 'money', self.player.money + 50000)),
                ("Bạn bị rơi mất 20,000 VNĐ.", lambda: setattr(self.player, 'money', max(0, self.player.money - 20000))),
                ("Thời tiết đẹp, tâm trạng của bạn trở nên Vui vẻ!", lambda: setattr(self.player, 'mood', 'Vui')),
                ("Bị kẹt xe đi làm muộn, bạn cảm thấy Buồn.", lambda: setattr(self.player, 'mood', 'Buồn')),
            ]
            event_text, action = random.choice(events)
            action()
            self.add_log(f"SỰ KIỆN: {event_text}")

    def check_achievements(self):
        # Simple achievement: have more than 5,000,000 VND
        if not hasattr(self, 'achieved_rich') and self.player.money >= 5000000:
            self.player.diamonds += 10
            self.add_log("THÀNH TỰU: Trở nên giàu có (Tiền > 5 triệu)! Thưởng 10 Kim cương.")
            self.achieved_rich = True

        # Achievement: survive 7 days
        days_passed = (self.game_time - datetime(2024, 1, 1, 8, 0, 0)).days
        if not hasattr(self, 'achieved_survivor') and days_passed >= 7:
            self.player.diamonds += 5
            self.add_log("THÀNH TỰU: Sống sót 1 tuần! Thưởng 5 Kim cương.")
            self.achieved_survivor = True

    def hospitalize(self):
        # Pause fast forward if any
        self.fast_forward = False
        self.fast_forward_callback = None

        hospital_fee = 5000000
        if self.player.money >= hospital_fee:
            self.player.money -= hospital_fee
            fee_str = f"đã trả {hospital_fee:,} VNĐ"
        else:
            self.player.debt += hospital_fee
            fee_str = f"nợ thêm {hospital_fee:,} VNĐ"

        self.player.health = 100
        self.player.hunger = 100
        self.player.thirst = 100
        self.player.mood = "Buồn"

        # Advance time by 3 days for treatment
        self.game_time += timedelta(days=3)
        self.add_log(f"Bạn đã ngất xỉu và nằm viện 3 ngày! Viện phí: {fee_str}.")

    def handle_monthly_bill(self):
        bill = 3000000
        if self.player.money >= bill:
            self.player.money -= bill
            self.add_log(f"Đã thanh toán tiền nhà/điện/nước: {bill:,} VNĐ")
        else:
            self.player.debt += bill
            self.add_log(f"Không đủ tiền trả hóa đơn. Nợ tăng thêm {bill:,} VNĐ")

    def draw_logs(self, surface):
        # Draw logs in the center
        log_x = 250
        log_y = 100
        log_w = 450
        log_h = 300
        pygame.draw.rect(surface, GRAY, (log_x, log_y, log_w, log_h), border_radius=10)
        pygame.draw.rect(surface, BLACK, (log_x, log_y, log_w, log_h), 2, border_radius=10)

        title_surf = font_md.render("Thông báo / Sự kiện", True, BLACK)
        surface.blit(title_surf, (log_x + 10, log_y + 10))

        y_offset = log_y + 45
        for log in self.logs:
            log_surf = font_sm.render(log, True, BLACK)
            surface.blit(log_surf, (log_x + 10, y_offset))
            y_offset += 25

    def draw(self, surface):
        surface.fill(WHITE)
        self.draw_avatar_and_time(surface)
        self.draw_money_and_stats(surface)
        self.draw_logs(surface)

        for btn in self.buttons:
            btn.draw(surface)

def main():
    game = Game()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEMOTION:
                for btn in game.buttons:
                    btn.check_hover(mouse_pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    for btn in game.buttons:
                        btn.handle_click(mouse_pos)

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

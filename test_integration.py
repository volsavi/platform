import unittest
import pygame
from platformer import Player, Platform, Coin  # Импортируем классы из основного кода

class TestIntegration(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.player = Player()
        self.platforms = [Platform(100, 700, 120, 20)]
        self.coins = [Coin(110, 670)]
    
    def test_player_lands_on_platform(self):
        """TC-01: Проверка, что игрок останавливается на платформе."""
        self.player.rect.y = 695  # Над платформой
        self.player.move(self.platforms)
        self.assertTrue(self.player.on_ground)
    
    def test_player_collects_coin(self):
        """TC-02: Проверка сбора монеты игроком."""
        self.player.rect.topleft = (110, 670)
        initial_score = self.player.score
        self.player.check_collision(self.coins)
        self.assertEqual(self.player.score, initial_score + 10)
    
    def test_player_falls_off_screen(self):
        """TC-03: Проверка, что падение за пределы экрана уменьшает здоровье."""
        initial_health = self.player.health
        self.player.rect.y = 900  # Упал за экран
        self.player.check_collision(self.coins)
        self.assertEqual(self.player.health, initial_health - 1)
    
    def test_player_dies_after_losing_all_health(self):
        """TC-04: Проверка, что игрок умирает после потери всего здоровья."""
        self.player.health = 1
        self.player.rect.y = 900
        game_over = self.player.check_collision(self.coins)
        self.assertTrue(game_over)
    
    def test_moving_platform_changes_position(self):
        """TC-05: Проверка движения платформы."""
        moving_platform = Platform(200, 600, 120, 20, moving=True)
        initial_x = moving_platform.rect.x
        moving_platform.move()
        self.assertNotEqual(moving_platform.rect.x, initial_x)
    
if __name__ == "__main__":
    unittest.main()

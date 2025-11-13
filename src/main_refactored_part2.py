"""
這是 main_refactored.py 的第二部分
包含：登入管理器、遊戲控制器、視窗管理器、主程式邏輯
"""

# ==================== 登入管理器 ====================


class LoginManager:
    """登入流程管理器"""
    
    def __init__(self, driver: WebDriver, credential: UserCredential):
        """
        初始化登入管理器
        
        Args:
            driver: WebDriver實例
            credential: 使用者憑證
        """
        self.driver = driver
        self.credential = credential
        self.username = credential.username
    
    def perform_login(self) -> bool:
        """
        執行登入操作
        
        Returns:
            bool: 登入成功返回True
            
        Raises:
            LoginError: 當登入失敗時
        """
        try:
            logger.info(f"[{self.username}] 開始登入...")
            
            # 輸入帳號
            username_input = self.driver.find_element(By.XPATH, ELEMENT_SELECTOR.USERNAME_INPUT)
            username_input.clear()
            username_input.send_keys(self.credential.username)
            
            # 輸入密碼
            password_input = self.driver.find_element(By.XPATH, ELEMENT_SELECTOR.PASSWORD_INPUT)
            password_input.clear()
            password_input.send_keys(self.credential.password)
            
            # 點擊登入按鈕
            login_button = self.driver.find_element(By.XPATH, ELEMENT_SELECTOR.LOGIN_BUTTON)
            login_button.click()
            
            time.sleep(5)
            
            logger.info(f"[{self.username}] 登入成功")
            return True
            
        except NoSuchElementException as e:
            raise LoginError(f"[{self.username}] 找不到登入元素: {e}") from e
        except Exception as e:
            raise LoginError(f"[{self.username}] 登入過程發生錯誤: {e}") from e
    
    def wait_for_image(self, template_path: Path, timeout: int = 60) -> bool:
        """
        等待圖片出現
        
        Args:
            template_path: 模板圖片路徑
            timeout: 超時時間（秒）
            
        Returns:
            bool: 在超時前找到返回True
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                screenshot = self.driver.get_screenshot_as_png()
                screenshot_np = ImageProcessor.screenshot_to_array(screenshot)
                screenshot_gray = ImageProcessor.to_grayscale(screenshot_np)
                
                matched, similarity, position = ImageProcessor.match_template(
                    screenshot_gray, 
                    template_path, 
                    GAME_CONFIG.image_match_threshold
                )
                
                if matched:
                    logger.debug(f"[{self.username}] 找到圖片 (相似度: {similarity:.3f})")
                    return True
                    
            except ImageDetectionError as e:
                logger.warning(f"[{self.username}] 圖片檢測錯誤: {e}")
            
            time.sleep(GAME_CONFIG.image_detect_interval)
        
        logger.warning(f"[{self.username}] 等待圖片超時 ({timeout}秒)")
        return False
    
    def wait_for_image_disappear(self, template_path: Path, timeout: int = 60) -> bool:
        """
        等待圖片消失
        
        Args:
            template_path: 模板圖片路徑
            timeout: 超時時間（秒）
            
        Returns:
            bool: 在超時前消失返回True
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                screenshot = self.driver.get_screenshot_as_png()
                screenshot_np = ImageProcessor.screenshot_to_array(screenshot)
                screenshot_gray = ImageProcessor.to_grayscale(screenshot_np)
                
                matched, _, _ = ImageProcessor.match_template(
                    screenshot_gray, 
                    template_path, 
                    GAME_CONFIG.image_match_threshold
                )
                
                if not matched:
                    logger.debug(f"[{self.username}] 圖片已消失")
                    return True
                    
            except ImageDetectionError as e:
                logger.warning(f"[{self.username}] 圖片檢測錯誤: {e}")
            
            time.sleep(GAME_CONFIG.image_detect_interval)
        
        logger.warning(f"[{self.username}] 等待圖片消失超時 ({timeout}秒)")
        return False
    
    def navigate_to_game(self) -> bool:
        """
        導航到遊戲頁面
        
        Returns:
            bool: 成功返回True
            
        Raises:
            LoginError: 當導航失敗時
        """
        try:
            logger.info(f"[{self.username}] 正在進入遊戲...")
            self.driver.get(URL_CONFIG.GAME_PAGE)
            time.sleep(3)
            
            # 設定視窗大小
            self.driver.set_window_size(WINDOW_CONFIG.width, WINDOW_CONFIG.height)
            
            # === 步驟 1: 等待 lobby_login.png 出現 ===
            logger.info(f"[{self.username}] 步驟 1: 正在檢測 lobby_login.png...")
            if not self.wait_for_image(
                path_manager.lobby_login_image, 
                GAME_CONFIG.image_detect_timeout
            ):
                raise LoginError(f"[{self.username}] 步驟 1 失敗：未檢測到 lobby_login.png")
            
            logger.info(f"[{self.username}] 步驟 1 完成：已確認 lobby_login.png 存在")
            
            # === 切入 iframe ===
            logger.info(f"[{self.username}] 正在切換到遊戲 iframe...")
            iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, ELEMENT_SELECTOR.GAME_IFRAME))
            )
            self.driver.switch_to.frame(iframe)
            logger.info(f"[{self.username}] 已成功切換到 iframe")
            
            # === 取得 Canvas 區域 ===
            logger.info(f"[{self.username}] 正在取得 Canvas 座標...")
            rect = self.driver.execute_script(f"""
                const canvas = document.getElementById('{ELEMENT_SELECTOR.GAME_CANVAS}');
                const r = canvas.getBoundingClientRect();
                return {{x: r.left, y: r.top, w: r.width, h: r.height}};
            """)
            logger.info(f"[{self.username}] Canvas 區域: x={rect['x']}, y={rect['y']}, w={rect['w']}, h={rect['h']}")
            
            # === 計算點擊座標 ===
            start_x = rect["x"] + rect["w"] * CLICK_COORD.START_GAME_X_RATIO
            start_y = rect["y"] + rect["h"] * CLICK_COORD.START_GAME_Y_RATIO
            confirm_x = rect["x"] + rect["w"] * CLICK_COORD.MACHINE_CONFIRM_X_RATIO
            confirm_y = rect["y"] + rect["h"] * CLICK_COORD.MACHINE_CONFIRM_Y_RATIO
            
            logger.info(f"[{self.username}] 開始遊戲按鈕座標: ({start_x:.1f}, {start_y:.1f})")
            logger.info(f"[{self.username}] 確認按鈕座標: ({confirm_x:.1f}, {confirm_y:.1f})")
            
            # === 步驟 2: 點擊開始遊戲按鈕 ===
            time.sleep(1)
            logger.info(f"[{self.username}] 步驟 2: 點擊開始遊戲按鈕...")
            self._click_coordinate(start_x, start_y)
            
            logger.info(f"[{self.username}] 步驟 2: 等待 lobby_login.png 消失...")
            if not self.wait_for_image_disappear(path_manager.lobby_login_image, 30):
                raise LoginError(f"[{self.username}] 步驟 2 失敗：lobby_login.png 未消失")
            
            logger.info(f"[{self.username}] 步驟 2 完成：lobby_login.png 已消失")
            
            # === 步驟 3: 等待 lobby_confirm.png 出現 ===
            logger.info(f"[{self.username}] 步驟 3: 正在檢測 lobby_confirm.png...")
            if not self.wait_for_image(path_manager.lobby_confirm_image, 30):
                raise LoginError(f"[{self.username}] 步驟 3 失敗：未檢測到 lobby_confirm.png")
            
            logger.info(f"[{self.username}] 步驟 3 完成：已確認 lobby_confirm.png 存在")
            
            # === 步驟 4: 點擊確認按鈕 ===
            time.sleep(1)
            logger.info(f"[{self.username}] 步驟 4: 點擊確認按鈕...")
            self._click_coordinate(confirm_x, confirm_y)
            
            logger.info(f"[{self.username}] 步驟 4: 等待 lobby_confirm.png 消失...")
            if not self.wait_for_image_disappear(path_manager.lobby_confirm_image, 30):
                raise LoginError(f"[{self.username}] 步驟 4 失敗：lobby_confirm.png 未消失")
            
            logger.info(f"[{self.username}] 步驟 4 完成：lobby_confirm.png 已消失")
            
            # === 步驟 5: 成功進入遊戲 ===
            logger.info(f"[{self.username}] 步驟 5: 已成功進入遊戲控制模式")
            time.sleep(2)
            return True
            
        except TimeoutException as e:
            raise LoginError(f"[{self.username}] 頁面載入超時: {e}") from e
        except Exception as e:
            if isinstance(e, LoginError):
                raise
            raise LoginError(f"[{self.username}] 導航到遊戲失敗: {e}") from e
    
    def _click_coordinate(self, x: float, y: float) -> None:
        """
        點擊指定座標
        
        Args:
            x: X座標
            y: Y座標
        """
        for event in ["mousePressed", "mouseReleased"]:
            self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": event,
                "x": x,
                "y": y,
                "button": "left",
                "clickCount": 1
            })
    
    @staticmethod
    def login_with_retry(driver: WebDriver, credential: UserCredential, 
                        max_retries: int = 3) -> bool:
        """
        帶重試的完整登入流程
        
        Args:
            driver: WebDriver實例
            credential: 使用者憑證
            max_retries: 最大重試次數
            
        Returns:
            bool: 登入成功返回True
        """
        manager = LoginManager(driver, credential)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"[{credential.username}] 開始登入流程（嘗試 {attempt + 1}/{max_retries}）")
                
                # 開啟登入頁面
                driver.get(URL_CONFIG.LOGIN_PAGE)
                time.sleep(2)
                
                # 執行登入
                manager.perform_login()
                time.sleep(2)
                
                # 導航到遊戲
                manager.navigate_to_game()
                
                logger.info(f"[{credential.username}] 登入流程成功完成")
                return True
                
            except LoginError as e:
                logger.error(f"[{credential.username}] 登入失敗（嘗試 {attempt + 1}/{max_retries}）: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"[{credential.username}] 準備重試...")
                    time.sleep(GAME_CONFIG.retry_delay)
                    continue
                logger.error(f"[{credential.username}] 已達最大重試次數，登入失敗")
                return False
            except Exception as e:
                logger.error(f"[{credential.username}] 未預期的錯誤: {e}")
                if attempt < max_retries - 1:
                    time.sleep(GAME_CONFIG.retry_delay)
                    continue
                return False
        
        return False


# ==================== 遊戲控制器 ====================


class GameController:
    """遊戲控制器"""
    
    def __init__(self, driver: WebDriver):
        """
        初始化遊戲控制器
        
        Args:
            driver: WebDriver實例
        """
        self.driver = driver
    
    def send_key(self, key_config: Dict[str, Any]) -> bool:
        """
        發送鍵盤事件
        
        Args:
            key_config: 按鍵配置
            
        Returns:
            bool: 成功返回True
        """
        try:
            for event_type in ["keyDown", "keyUp"]:
                self.driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
                    "type": event_type,
                    "key": key_config["key"],
                    "code": key_config["code"],
                    "windowsVirtualKeyCode": key_config["windowsVirtualKeyCode"],
                    "nativeVirtualKeyCode": key_config["nativeVirtualKeyCode"]
                })
            return True
        except Exception as e:
            logger.warning(f"發送按鍵失敗: {e}")
            return False
    
    def send_space(self) -> bool:
        """發送空白鍵"""
        return self.send_key(KEYBOARD_KEY.SPACE)
    
    def send_arrow_left(self) -> bool:
        """發送左方向鍵"""
        logger.debug("發送左方向鍵")
        return self.send_key(KEYBOARD_KEY.ARROW_LEFT)
    
    def send_arrow_right(self) -> bool:
        """發送右方向鍵"""
        logger.debug("發送右方向鍵")
        return self.send_key(KEYBOARD_KEY.ARROW_RIGHT)
    
    def switch_to_game_frame(self) -> bool:
        """切換到遊戲iframe"""
        try:
            self.driver.switch_to.default_content()
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                self.driver.switch_to.frame(iframes[0])
                logger.info("已切換到遊戲 iframe")
                return True
        except Exception as e:
            logger.debug(f"切換 iframe 失敗: {e}")
        return False
    
    def get_current_betsize(self) -> Optional[float]:
        """
        取得當前下注金額
        
        Returns:
            Optional[float]: 當前金額，失敗返回None
        """
        try:
            logger.info("開始查詢當前下注金額...")
            
            # 截取整個瀏覽器截圖
            screenshot = self.driver.get_screenshot_as_png()
            screenshot_np = ImageProcessor.screenshot_to_array(screenshot)
            screenshot_gray = ImageProcessor.to_grayscale(screenshot_np)
            
            # 與資料夾中的圖片進行比對
            matched_amount = self._compare_betsize_images(screenshot_gray)
            
            if matched_amount:
                try:
                    amount_value = float(matched_amount)
                    if amount_value in GAME_BETSIZE:
                        logger.info(f"當前下注金額: {amount_value}")
                        return amount_value
                    else:
                        logger.warning(f"金額 {matched_amount} 不在 GAME_BETSIZE 列表中")
                except ValueError:
                    logger.error(f"無法將 {matched_amount} 轉換為數字")
            else:
                logger.warning("無法識別當前下注金額")
            
            return None
            
        except Exception as e:
            logger.error(f"查詢下注金額時發生錯誤: {e}")
            return None
    
    def _compare_betsize_images(self, screenshot_gray: np.ndarray) -> Optional[str]:
        """
        使用 bet_size 資料夾中的圖片比對
        
        Args:
            screenshot_gray: 截圖（灰階）
            
        Returns:
            Optional[str]: 匹配的金額
        """
        try:
            bet_size_dir = path_manager.bet_size_dir
            if not bet_size_dir.exists():
                logger.error(f"bet_size 資料夾不存在: {bet_size_dir}")
                return None
            
            # 取得所有 png 圖片
            image_files = sorted(bet_size_dir.glob("*.png"))
            if not image_files:
                logger.warning(f"bet_size 資料夾中沒有圖片")
                return None
            
            logger.info(f"開始比對 {len(image_files)} 張圖片...")
            
            best_match_score = 0.0
            best_match_amount = None
            
            for image_file in image_files:
                matched, similarity, _ = ImageProcessor.match_template(
                    screenshot_gray,
                    image_file,
                    GAME_CONFIG.image_match_threshold
                )
                
                logger.debug(f"圖片 {image_file.name} 匹配度：{similarity:.3f}")
                
                if similarity > best_match_score:
                    best_match_score = similarity
                    best_match_amount = image_file.stem
            
            if best_match_score >= GAME_CONFIG.image_match_threshold:
                logger.info(f"找到匹配金額：{best_match_amount} (相似度：{best_match_score:.3f})")
                return best_match_amount
            else:
                logger.warning(f"未找到匹配圖片 (最高相似度：{best_match_score:.3f})")
                return None
                
        except Exception as e:
            logger.error(f"比對圖片時發生錯誤: {e}")
            return None
    
    def adjust_betsize(self, target_amount: float, max_attempts: int = 200) -> bool:
        """
        調整下注金額到目標值
        
        Args:
            target_amount: 目標金額
            max_attempts: 最大嘗試次數
            
        Returns:
            bool: 調整成功返回True
            
        Raises:
            GameControlError: 當調整失敗時
        """
        try:
            # 檢查目標金額
            if target_amount not in GAME_BETSIZE:
                raise GameControlError(f"目標金額 {target_amount} 不在可用金額列表中")
            
            logger.info(f"目標金額: {target_amount}")
            
            # 取得當前金額
            current_amount = self.get_current_betsize()
            if current_amount is None:
                raise GameControlError("無法識別當前金額")
            
            logger.info(f"當前金額: {current_amount}")
            
            # 檢查是否已是目標金額
            if current_amount == target_amount:
                logger.info("當前金額已是目標金額，無需調整")
                return True
            
            # 計算需要調整的次數和方向
            current_index = GAME_BETSIZE.index(current_amount)
            target_index = GAME_BETSIZE.index(target_amount)
            diff = target_index - current_index
            
            if diff > 0:
                click_func = self.send_arrow_right
                direction = "增加"
                estimated_steps = diff
            else:
                click_func = self.send_arrow_left
                direction = "減少"
                estimated_steps = abs(diff)
            
            logger.info(f"預估需要點擊{direction}按鈕約 {estimated_steps} 次")
            
            # 開始調整
            for i in range(estimated_steps):
                click_func()
                logger.info(f"已點擊 {direction} 按鈕 ({i + 1}/{estimated_steps})")
                time.sleep(0.3)
            
            time.sleep(1)
            
            # 驗證並微調
            logger.info("開始驗證調整結果...")
            for attempt in range(max_attempts):
                current_amount = self.get_current_betsize()
                
                if current_amount is None:
                    logger.warning(f"驗證失敗：無法識別金額 (嘗試 {attempt + 1}/{max_attempts})")
                    time.sleep(0.5)
                    continue
                
                if current_amount == target_amount:
                    logger.info(f"✓ 調整成功! 當前金額: {current_amount}")
                    return True
                
                logger.info(f"當前金額 {current_amount}，目標 {target_amount}，繼續調整...")
                
                if current_amount < target_amount:
                    self.send_arrow_right()
                else:
                    self.send_arrow_left()
                
                time.sleep(0.5)
            
            raise GameControlError(f"調整失敗，已達最大嘗試次數 ({max_attempts})")
            
        except Exception as e:
            if isinstance(e, GameControlError):
                raise
            raise GameControlError(f"調整金額時發生錯誤: {e}") from e
    
    def take_screenshot(self) -> bool:
        """
        截取螢幕並保存到桌面
        
        Returns:
            bool: 成功返回True
        """
        try:
            from datetime import datetime
            
            desktop_path = Path.home() / "Desktop"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = desktop_path / filename
            
            screenshot = self.driver.get_screenshot_as_png()
            
            with open(filepath, 'wb') as f:
                f.write(screenshot)
            
            logger.info(f"✓ 截圖已儲存至：{filepath}")
            return True
            
        except Exception as e:
            logger.error(f"截圖失敗：{e}")
            return False
    
    def peek_betsize(self, target_amount: float) -> bool:
        """
        檢測指定金額的圖片是否存在
        
        Args:
            target_amount: 要檢測的金額
            
        Returns:
            bool: 找到返回True
        """
        try:
            if target_amount not in GAME_BETSIZE:
                logger.error(f"金額 {target_amount} 不在 GAME_BETSIZE 列表中")
                return False
            
            logger.info(f"開始檢測金額 {target_amount} 的圖片...")
            
            screenshot = self.driver.get_screenshot_as_png()
            screenshot_np = ImageProcessor.screenshot_to_array(screenshot)
            screenshot_gray = ImageProcessor.to_grayscale(screenshot_np)
            
            template_path = path_manager.bet_size_dir / f"{target_amount}.png"
            
            if not template_path.exists():
                logger.error(f"找不到金額 {target_amount} 的圖片：{template_path}")
                return False
            
            matched, similarity, position = ImageProcessor.match_template(
                screenshot_gray,
                template_path,
                GAME_CONFIG.image_match_threshold
            )
            
            logger.info(f"金額 {target_amount} 的匹配度：{similarity:.3f}")
            logger.info(f"匹配位置：{position}")
            
            if matched:
                logger.info(f"✓ 找到金額 {target_amount} 的圖片！(相似度：{similarity:.3f})")
                return True
            else:
                logger.info(f"✗ 未找到金額 {target_amount} 的圖片 (相似度：{similarity:.3f})")
                return False
                
        except Exception as e:
            logger.error(f"檢測金額圖片時發生錯誤：{e}")
            return False


# ==================== 遊戲執行器 ====================


class GameExecutor:
    """遊戲執行器"""
    
    def __init__(self, driver: WebDriver):
        """
        初始化遊戲執行器
        
        Args:
            driver: WebDriver實例
        """
        self.driver = driver
        self.controller = GameController(driver)
    
    def execute_with_rules(self) -> None:
        """按規則執行遊戲"""
        try:
            # 切換到遊戲 iframe
            self.controller.switch_to_game_frame()
            
            # 取得規則列表
            rules = game_state_manager.get_rules(self.driver)
            
            if not rules:
                logger.warning("沒有可用的遊戲規則，使用預設模式")
                self._execute_default_mode()
                return
            
            # 按規則執行
            for rule_idx, rule in enumerate(rules, 1):
                if not game_state_manager.is_running(self.driver):
                    logger.info("遊戲已暫停")
                    break
                
                logger.info(f"開始執行規則 {rule_idx}/{len(rules)}: 金額 {rule.betsize}, 持續 {rule.duration_minutes} 分鐘")
                
                # 調整金額
                try:
                    if not self.controller.adjust_betsize(rule.betsize):
                        logger.error(f"調整金額失敗，跳過規則 {rule_idx}")
                        continue
                except GameControlError as e:
                    logger.error(f"調整金額錯誤：{e}，跳過規則 {rule_idx}")
                    continue
                
                logger.info(f"金額已調整為 {rule.betsize}，開始執行 {rule.duration_minutes} 分鐘")
                
                # 計算結束時間
                end_time = time.time() + rule.duration_seconds
                press_count = 0
                
                # 在指定時間內持續按空白鍵
                while time.time() < end_time:
                    if not game_state_manager.is_running(self.driver):
                        logger.info("遊戲已暫停")
                        return
                    
                    self.controller.send_space()
                    press_count += 1
                    
                    remaining_seconds = int(end_time - time.time())
                    logger.info(f"規則 {rule_idx}: 已按 {press_count} 次，剩餘 {remaining_seconds} 秒")
                    
                    # 使用小間隔檢查狀態
                    for _ in range(GAME_CONFIG.key_interval):
                        if not game_state_manager.is_running(self.driver):
                            logger.info("遊戲已暫停")
                            return
                        if time.time() >= end_time:
                            break
                        time.sleep(1)
                
                logger.info(f"規則 {rule_idx} 執行完成（共按 {press_count} 次空白鍵）")
            
            logger.info("所有規則執行完畢，遊戲停止")
            game_state_manager.set_running(self.driver, False)
            
        except Exception as e:
            logger.error(f"遊戲執行發生錯誤：{e}")
        finally:
            game_state_manager.set_running(self.driver, False)
            game_state_manager.set_thread(self.driver, None)
    
    def _execute_default_mode(self) -> None:
        """執行預設模式（每15秒按一次空白鍵）"""
        logger.info("使用預設模式執行遊戲")
        
        while True:
            if not game_state_manager.is_running(self.driver):
                break
            
            self.controller.send_space()
            
            # 使用小間隔檢查狀態
            for _ in range(GAME_CONFIG.key_interval):
                if not game_state_manager.is_running(self.driver):
                    break
                time.sleep(1)


# ==================== 視窗管理器 ====================


class WindowManager:
    """視窗管理器"""
    
    @staticmethod
    def arrange_windows(drivers: List[Optional[WebDriver]]) -> int:
        """
        按網格模式排列視窗
        
        Args:
            drivers: WebDriver實例列表
            
        Returns:
            int: 成功排列的視窗數量
        """
        valid_drivers = [d for d in drivers if d is not None]
        if not valid_drivers:
            logger.warning("沒有有效的瀏覽器實例需要排列")
            return 0
        
        logger.info(f"開始排列 {len(valid_drivers)} 個瀏覽器視窗...")
        success_count = 0
        
        for index, driver in enumerate(valid_drivers):
            try:
                # 計算視窗位置
                col = index % WINDOW_CONFIG.columns
                row = (index // WINDOW_CONFIG.columns) % WINDOW_CONFIG.rows
                
                x_position = col * WINDOW_CONFIG.width
                y_position = row * WINDOW_CONFIG.height
                
                # 設定視窗位置和大小
                driver.set_window_position(x_position, y_position)
                driver.set_window_size(WINDOW_CONFIG.width, WINDOW_CONFIG.height)
                
                logger.info(f"瀏覽器 #{index + 1} 已移動到位置 ({x_position}, {y_position})")
                success_count += 1
            except Exception as e:
                logger.warning(f"無法排列瀏覽器 #{index + 1}：{e}")
        
        logger.info(f"瀏覽器視窗排列完成（成功：{success_count}/{len(valid_drivers)}）")
        return success_count


# ==================== 主程式控制器 ====================


class MainController:
    """主程式控制器"""
    
    def __init__(self):
        """初始化主程式控制器"""
        self.drivers: List[Optional[WebDriver]] = []
        self.credentials: List[UserCredential] = []
    
    def load_configurations(self) -> bool:
        """
        載入配置
        
        Returns:
            bool: 成功返回True
        """
        try:
            self.credentials = ConfigLoader.load_credentials()
            return True
        except ConfigurationError as e:
            logger.error(f"載入配置失敗: {e}")
            return False
    
    def get_browser_count(self) -> Optional[int]:
        """
        取得使用者輸入的瀏覽器數量
        
        Returns:
            Optional[int]: 瀏覽器數量，取消返回None
        """
        max_allowed = min(GAME_CONFIG.max_accounts, len(self.credentials))
        
        while True:
            try:
                count = int(input(f"請輸入要啟動的瀏覽器數量 (1~{max_allowed})："))
                if 1 <= count <= max_allowed:
                    return count
                logger.warning(f"請輸入介於 1 到 {max_allowed} 的整數")
            except ValueError:
                logger.warning("請輸入有效的整數")
            except (EOFError, KeyboardInterrupt):
                logger.info("\n程式已中止")
                return None
    
    def launch_browsers(self, count: int) -> int:
        """
        並行啟動多個瀏覽器
        
        Args:
            count: 要啟動的數量
            
        Returns:
            int: 成功啟動的數量
        """
        self.drivers = [None] * count
        threads = []
        
        def launch_worker(index: int) -> None:
            """執行緒工作函式"""
            credential = self.credentials[index]
            try:
                driver = BrowserManager.create_webdriver(credential.proxy)
                if LoginManager.login_with_retry(driver, credential):
                    self.drivers[index] = driver
                else:
                    if driver:
                        driver.quit()
            except Exception as e:
                logger.error(f"[{credential.username}] 啟動失敗: {e}")
        
        logger.info(f"開始啟動 {count} 個瀏覽器...")
        
        for i in range(count):
            logger.info(f"啟動第 {i + 1} 個瀏覽器（帳號：{self.credentials[i].username}）")
            thread = threading.Thread(target=launch_worker, args=(i,), daemon=True)
            threads.append(thread)
            thread.start()
        
        logger.info("等待所有瀏覽器啟動完成...")
        for thread in threads:
            thread.join()
        
        success_count = sum(1 for d in self.drivers if d is not None)
        logger.info(f"完成！成功啟動 {success_count}/{count} 個瀏覽器")
        
        return success_count
    
    def start_game(self, driver: WebDriver) -> bool:
        """
        開始遊戲
        
        Args:
            driver: WebDriver實例
            
        Returns:
            bool: 成功返回True
        """
        if game_state_manager.is_running(driver):
            logger.info("遊戲已在執行中")
            return False
        
        # 載入遊戲規則
        try:
            rules = ConfigLoader.load_game_rules()
            game_state_manager.set_rules(driver, rules)
            
            if rules:
                logger.info(f"已載入 {len(rules)} 條遊戲規則")
                
                # 檢查並調整到第一條規則的金額
                controller = GameController(driver)
                controller.switch_to_game_frame()
                
                first_rule_betsize = rules[0].betsize
                logger.info(f"檢查當前金額是否符合第一條規則的金額 {first_rule_betsize}...")
                
                current_amount = controller.get_current_betsize()
                if current_amount:
                    logger.info(f"當前金額: {current_amount}")
                    
                    if current_amount != first_rule_betsize:
                        logger.info(f"當前金額 {current_amount} 不符合規則金額 {first_rule_betsize}，開始調整...")
                        try:
                            if not controller.adjust_betsize(first_rule_betsize):
                                logger.error("調整金額失敗，無法開始遊戲")
                                return False
                            logger.info(f"✓ 金額已調整為 {first_rule_betsize}")
                        except GameControlError as e:
                            logger.error(f"調整金額錯誤：{e}，無法開始遊戲")
                            return False
                    else:
                        logger.info("✓ 當前金額已符合規則要求")
                else:
                    logger.warning("無法識別當前金額，將嘗試調整到目標金額")
                    try:
                        if not controller.adjust_betsize(first_rule_betsize):
                            logger.error("調整金額失敗，無法開始遊戲")
                            return False
                    except GameControlError as e:
                        logger.error(f"調整金額錯誤：{e}，無法開始遊戲")
                        return False
        except ConfigurationError as e:
            logger.error(f"載入規則失敗：{e}，將使用預設模式")
            game_state_manager.set_rules(driver, None)
        
        # 啟動遊戲執行緒
        game_state_manager.set_running(driver, True)
        executor = GameExecutor(driver)
        game_thread = threading.Thread(target=executor.execute_with_rules, daemon=True)
        game_state_manager.set_thread(driver, game_thread)
        game_thread.start()
        
        logger.info("遊戲已開始執行")
        return True
    
    def pause_game(self, driver: WebDriver) -> bool:
        """
        暫停遊戲
        
        Args:
            driver: WebDriver實例
            
        Returns:
            bool: 成功返回True
        """
        if not game_state_manager.is_running(driver):
            logger.info("遊戲未在執行中")
            return False
        
        game_state_manager.set_running(driver, False)
        logger.info("已發送暫停信號")
        
        thread = game_state_manager.get_thread(driver)
        if thread and thread.is_alive():
            thread.join(timeout=3)
        
        logger.info("遊戲已暫停")
        return True
    
    def quit_browser(self, driver: WebDriver) -> bool:
        """
        關閉瀏覽器
        
        Args:
            driver: WebDriver實例
            
        Returns:
            bool: 成功返回True
        """
        try:
            self.pause_game(driver)
            driver.quit()
            logger.info("瀏覽器已關閉")
            game_state_manager.remove(driver)
            return True
        except Exception as e:
            err_msg = str(e)
            if "Remote end closed connection" not in err_msg and "chrome not reachable" not in err_msg.lower():
                logger.warning(f"關閉瀏覽器時發生錯誤：{e}")
            return False
    
    def cleanup_all(self) -> None:
        """清理所有資源"""
        logger.info("正在停止所有遊戲...")
        for driver in self.drivers:
            if driver is not None:
                self.pause_game(driver)
        
        logger.info("正在關閉所有瀏覽器...")
        for driver in self.drivers:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    pass
        
        game_state_manager.cleanup_all()
        logger.info("清理完成")
    
    def process_command(self, command: str) -> bool:
        """
        處理使用者指令
        
        Args:
            command: 指令字串
            
        Returns:
            bool: 是否應該退出程式
        """
        command = command.lower().strip()
        
        if command == GameCommand.QUIT.value:
            self.cleanup_all()
            return True
        
        if command == GameCommand.CONTINUE.value:
            for driver in self.drivers:
                if driver is not None:
                    self.start_game(driver)
        
        elif command == GameCommand.SCREENSHOT.value:
            for driver in self.drivers:
                if driver is not None:
                    GameController(driver).take_screenshot()
        
        elif command.startswith(GameCommand.PEEK.value):
            parts = command.split()
            if len(parts) < 2:
                logger.warning("請輸入要檢測的金額，格式: p <金額>")
                logger.info(f"可用金額: {GAME_BETSIZE}")
            else:
                try:
                    target_amount = float(parts[1])
                    for driver in self.drivers:
                        if driver is not None:
                            GameController(driver).peek_betsize(target_amount)
                except ValueError:
                    logger.error(f"無效的金額: {parts[1]}")
        
        elif command.startswith(GameCommand.BET_SIZE.value):
            parts = command.split()
            if len(parts) < 2:
                logger.warning("請輸入目標金額，格式: b <金額>")
                logger.info(f"可用金額: {GAME_BETSIZE}")
            else:
                try:
                    target_amount = float(parts[1])
                    for driver in self.drivers:
                        if driver is not None:
                            try:
                                GameController(driver).adjust_betsize(target_amount)
                            except GameControlError as e:
                                logger.error(f"調整金額失敗：{e}")
                except ValueError:
                    logger.error(f"無效的金額: {parts[1]}")
        
        elif command == GameCommand.HELP.value or command == '?':
            self._show_help()
        
        else:
            logger.warning(f"未識別的指令：{command}")
            logger.info("輸入 'h' 或 '?' 查看幫助")
        
        return False
    
    def _show_help(self) -> None:
        """顯示幫助信息"""
        help_text = """
可用指令：
  c            - 繼續遊戲（開始自動執行）
  p            - 暫停遊戲
  b <金額>     - 調整下注金額，例如: b 2.4
  p <金額>     - 檢測指定金額圖片，例如: p 1.2
  s            - 截取螢幕
  q            - 退出程式
  h 或 ?       - 顯示此幫助信息

可用金額列表:
  0.4, 0.8, 1, 1.2, 1.6, 2, 2.4, 2.8, 3, 3.2, 3.6, 4, 5, 6, 7, 8, 9, 10,
  12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 60, 64, 72, 80, 100,
  120, 140, 160, 180, 200, 240, 280, 300, 320, 360, 400, 420, 480, 500,
  540, 560, 600, 640, 700, 720, 800, 840, 900, 960, 980, 1000, 1080,
  1120, 1200, 1260, 1280, 1400, 1440, 1600, 1800, 2000
        """
        print(help_text)
    
    def run_command_loop(self) -> None:
        """執行指令控制迴圈"""
        logger.info("已進入指令模式")
        self._show_help()
        
        try:
            while True:
                try:
                    command = input("\n請輸入指令：").strip()
                except EOFError:
                    logger.info("接收到 EOF，程式結束")
                    break
                
                if not command:
                    logger.warning("指令不能為空白，請重新輸入")
                    continue
                
                if self.process_command(command):
                    break
        
        except KeyboardInterrupt:
            logger.info("\n偵測到中斷訊號 (Ctrl+C)")
            self.cleanup_all()
    
    def run(self) -> None:
        """執行主程式"""
        logger.info("=== 金富翁遊戲自動化系統（專業重構版） ===")
        
        try:
            # 階段 1：載入配置
            if not self.load_configurations():
                return
            
            # 階段 2：取得使用者輸入
            browser_count = self.get_browser_count()
            if browser_count is None:
                return
            
            # 階段 3：啟動瀏覽器
            success_count = self.launch_browsers(browser_count)
            if success_count == 0:
                logger.error("沒有成功啟動任何瀏覽器，程式結束")
                return
            
            # 階段 4：排列視窗
            WindowManager.arrange_windows(self.drivers)
            
            # 階段 5：指令控制
            self.run_command_loop()
            
        except KeyboardInterrupt:
            logger.info("\n程式已中斷")
        except Exception as e:
            logger.error(f"程式執行錯誤：{e}", exc_info=True)
        finally:
            logger.info("程式結束")


# ==================== 程式入口 ====================


def main() -> None:
    """主程式入口"""
    controller = MainController()
    controller.run()


if __name__ == "__main__":
    main()

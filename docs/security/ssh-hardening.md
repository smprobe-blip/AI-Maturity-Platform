# SSH Hardening — audit.netbrainpower.ru

Применено: 2026-08-21

## Что настроено

### 1. Отключена парольная аутентификация
"
"

PasswordAuthentication no
PermitEmptyPasswords no
KbdInteractiveAuthentication no

Боты-переборщики больше не могут даже попытаться подобрать пароль.

### 2. Root-доступ только по ключу

PermitRootLogin prohibit-password


### 3. Fail2ban
- **5 неудачных попыток** → бан на **2 часа**
- Лог: `/var/log/fail2ban.log`
- Команды управления:
  ```bash
  # Статус
  sudo fail2ban-client status sshd
  
  # Разблокировать IP
  sudo fail2ban-client set sshd unbanip 1.2.3.4
  
  # Разблокировать все
  sudo fail2ban-client unban --all

PermitRootLogin prohibit-password



### 3. Fail2ban
- **5 неудачных попыток** → бан на **2 часа**
- Лог: `/var/log/fail2ban.log`
- Команды управления:
  ```bash
  # Статус
  sudo fail2ban-client status sshd
  
  # Разблокировать IP
  sudo fail2ban-client set sshd unbanip 1.2.3.4
  
  # Разблокировать все
  sudo fail2ban-client unban --all

4. Современные алгоритмы
KexAlgorithms: curve25519-sha256, diffie-hellman-group16/18-sha512
Ciphers: chacha20-poly1305, aes256-gcm, aes-gcm
MACs: hmac-sha2-*-etm
5. CI/CD пользователь deployer
Права: sudo /opt/deploy.sh без пароля
Ключ: /home/deployer/.ssh/id_ed25519
Группа: docker (для docker compose)
Аварийный доступ
Если потеряли SSH:
Веб-консоль Timeweb: Панель → Виртуальные серверы → Консоль
Вход как root → fail2ban-client set sshd unbanip ВАШ_IP
Файлы конфигурации
/etc/ssh/sshd_config.d/99-hardening.conf — основные настройки
/etc/fail2ban/jail.local — правила fail2ban
/etc/sudoers.d/deployer — права deployer
/home/deployer/.ssh/authorized_keys — ключ deployer
Откат


# Временно включить пароли
echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config.d/99-hardening.conf
systemctl restart sshd



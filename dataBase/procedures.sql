CREATE OR REPLACE PROCEDURE register_user(
    p_login TEXT,
    p_password TEXT,
    p_email TEXT,
    p_is_admin BOOLEAN,
    p_direction_id INTEGER,
    p_group_id INTEGER
) RETURNS INTEGER AS $$
DECLARE
    new_user_id INTEGER;
BEGIN
    -- Проверка уникальности логина и email
    IF EXISTS (SELECT 1 FROM users WHERE login = p_login) THEN
        RAISE EXCEPTION 'Пользователь с таким логином уже существует';
    END IF;
    
    IF EXISTS (SELECT 1 FROM users WHERE email = p_email) THEN
        RAISE EXCEPTION 'Пользователь с таким email уже существует';
    END IF;
    
    -- Вставка в таблицу users
    INSERT INTO users (login, password, is_admin, email, direction_id, created_at)
    VALUES (p_login, p_password, FALSE, p_email, p_direction_id, NOW())
    RETURNING user_id INTO new_user_id;
    
    -- Если это студент (не админ), добавляем запись в students
    IF NOT p_is_admin AND p_group_id IS NOT NULL THEN
        INSERT INTO students (user_id, group_id)
        VALUES (new_user_id, p_group_id);
    END IF;
    
    RETURN new_user_id;
END;
$$ LANGUAGE plpgsql;
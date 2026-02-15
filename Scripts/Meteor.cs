using UnityEngine;

public class Meteor : MonoBehaviour
{
    [Header("Налаштування руху")]
    public float speed = 3f;           // Швидкість польоту метеорита
    private Vector3 targetDirection;   // Напрямок, куди він летить

    void Start()
    {
        // 1. Шукаємо літачок за тегом "Player"
        GameObject player = GameObject.FindGameObjectWithTag("Player");

        if (player != null)
        {
            // 2. Рахуємо вектор напрямку від метеорита до гравця
            targetDirection = (player.transform.position - transform.position).normalized;
        }
        else
        {
            // 3. Якщо гравця не знайдено (наприклад, видалили), летимо просто вниз
            targetDirection = Vector3.down;
            Debug.LogWarning("Увага: Об'єкт з тегом 'Player' не знайдено!");
        }

        // 4. Автоматично видаляємо метеорит через 15 секунд, щоб не лагала гра
        Destroy(gameObject, 15f);
    }

    void Update()
    {
        // 5. Рухаємо метеорит у вибраному напрямку з заданою швидкістю
        transform.position += targetDirection * speed * Time.deltaTime;
    }
}
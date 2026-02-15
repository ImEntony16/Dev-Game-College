using UnityEngine;

public class Bullet : MonoBehaviour
{
    public float speed = 20f; // швидкість кулі [cite: 29]
    public float lifeTime = 10f; // автоматичне знищення через 10 сек [cite: 30]

    void Start()
    {
        // Знищуємо об'єкт через певний час [cite: 30]
        Destroy(gameObject, lifeTime);
    }

    void Update()
        {
        // Куля летить вперед у напрямку погляду літачка [cite: 29]
        transform.Translate(Vector3.up * speed * Time.deltaTime);
    }
}
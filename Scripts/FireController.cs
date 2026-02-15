using UnityEngine;

public class FireController : MonoBehaviour
{
    public GameObject bulletPrefab; // Префаб кулі з папки Assets
    public Transform firePoint;     // Об'єкт FirePoint на літачку
    public float fireRate = 0.5f;   // Інтервал стрільби [cite: 33]
    private float nextFireTime = 0f;

    void Update()
    {
        // Перевірка, чи настав час для наступного пострілу [cite: 33]
        if (Time.time >= nextFireTime)
        {
            Shoot();
            nextFireTime = Time.time + fireRate;
        }
    }

    void Shoot()
    {
        // Створення кулі в позиції firePoint з поворотом літачка [cite: 34, 35]
        if (bulletPrefab != null && firePoint != null)
        {
            Instantiate(bulletPrefab, firePoint.position, transform.rotation);
        }
    }
}
using UnityEngine;

public class MeteorSpawner : MonoBehaviour
{
    public GameObject meteorPrefab;
    public float spawnInterval = 2f;

    void Start()
    {
        InvokeRepeating("CreateMeteor", 1f, spawnInterval);
    }

    void CreateMeteor()
    {
        if (meteorPrefab != null)
        {
            // Випадкова позиція 
            Vector3 spawnPos = new Vector3(Random.Range(-8f, 8f), 6f, 0f);
            Instantiate(meteorPrefab, spawnPos, Quaternion.identity);
        }
    }
}
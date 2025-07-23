package com.example.eventbook

import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface EventApiService {
        @GET("events/{eventId}")
         suspend fun getEvent(@Path("eventId") eventId: Int): Response<EventResponse>

        @POST("events/{eventId}/rsvp")
        suspend fun rsvpEvent(@Path("eventId") eventId: Int, @Body request: RSVPRequest): Response<MessageResponse>
        @DELETE("events/{eventId}/rsvp")
        suspend fun cancelRsvp(@Path("eventId") eventId: Int, @Body request: RSVPRequest): Response<MessageResponse>
}
object RetrofitClient {
    private const val BASE_URL = "http://10.0.2.2:8000/" // Update for your backend
    val eventApiService: EventApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(EventApiService::class.java)
    }
}
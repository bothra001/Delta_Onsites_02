package com.example.eventbook

data class EventResponse(

   val name: String,
    val description: String?,
    val remaining_seats: Int,
    val registration_deadline: String,
    val registeredUsers: List<String>,
    val waitlistUsers: List<String>
)
data class RSVPRequest(
    val email: String
)
data class MessageResponse(
    val message: String
)
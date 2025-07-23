package com.example.eventbook

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@Composable
fun EventRSVPScreen(eventId: Int) {
    val coroutineScope = rememberCoroutineScope()

    var event by remember { mutableStateOf<EventResponse?>(null) }
    var email by remember { mutableStateOf("") }
    var message by remember { mutableStateOf("") }

    // Fetch event details dynamically
    LaunchedEffect(eventId) {
        coroutineScope.launch {
            message = ""
            try {
                val response = withContext(Dispatchers.IO) {
                    RetrofitClient.eventApiService.getEvent(eventId)
                }
                if (response.isSuccessful) {
                    event = response.body()
                } else {
                    message = "Error: ${response.message()}"
                }
            } catch (e: Exception) {
                message = "Network error: ${e.localizedMessage}"
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(
                        Color(0xFFFFF176),
                        Color(0xFFFFEB3B),
                        Color(0xFFBDBDBD),
                        Color.Black
                    ))),


                verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        event?.let {
            Text("Event: ${it.name}", style = MaterialTheme.typography.headlineSmall)
            Text("Description: ${it.description ?: "No description"}")
            Text("Remaining Seats: ${it.remaining_seats}")
            Text("Deadline: ${it.registration_deadline}")
            Text("Registered: ${it.registeredUsers.joinToString(", ")}")
            Text("Waitlist: ${it.waitlistUsers.joinToString(", ")}")
        }

        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Your Email") },
            modifier = Modifier.fillMaxWidth()
                .align (Alignment.CenterHorizontally)
        )

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick = {
                    coroutineScope.launch {
                        try {
                            val response = withContext(Dispatchers.IO) {
                                RetrofitClient.eventApiService.rsvpEvent(eventId, RSVPRequest(email))
                            }
                            message = response.body()?.message ?: "RSVP successful"
                        } catch (e: Exception) {
                            message = "RSVP failed: ${e.localizedMessage}"
                        }
                    }
                },
                modifier = Modifier.weight(1f)
            ) {
                Text("RSVP")
            }

            Button(
                onClick = {
                    coroutineScope.launch {
                        try {
                            val response = withContext(Dispatchers.IO) {
                                RetrofitClient.eventApiService.cancelRsvp(eventId, RSVPRequest(email))
                            }
                            message = response.body()?.message ?: "Cancellation successful"
                        } catch (e: Exception) {
                            message = "Cancel failed: ${e.localizedMessage}"
                        }
                    }
                },
                modifier = Modifier.weight(1f)
            ) {
                Text("Cancel RSVP")
            }
        }

        if (message.isNotEmpty()) {
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.error
            )
        }
    }
}







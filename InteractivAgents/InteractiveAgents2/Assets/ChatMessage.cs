
namespace Assets
{
    public class ChatMessage
    {
        public string Text;
        public string User;
        public UnityEngine.Texture2D Image;
        public string ImagePath;

        public ChatMessage(string text, string user, UnityEngine.Texture2D image = null, string imagePath = null)
        {
            Text = text;
            User = user;
            Image = image;
            ImagePath = imagePath;
        }
    }
}
